"""
TMDB Poster Bot — powered by Kurigram (Pyrogram fork)
Fetches movie & TV show posters from The Movie Database (TMDB).

User commands:
  /start          – Welcome message with image
  /help           – Help & tips
  /about          – About this bot
  /movie RRR 2022 – Movie poster (optional year)
  /tv Asur 2      – TV season poster (optional season)
  /search Title   – Auto-detect movie or TV show
  plain text      – Quick search

Admin commands:
  /stats          – Bot statistics
  /admins         – List all admins
  /ban <id>       – Ban a user
  /unban <id>     – Unban a user
  /banned         – List banned users
  /broadcast      – Broadcast to all users (reply to a message)
  /addfsub <id>   – Add force subscribe channel
  /delfsub <id>   – Remove force subscribe channel
  /listfsub       – List force subscribe channels

Owner-only commands:
  /addadmin <id>  – Add an admin
  /deladmin <id>  – Remove an admin
"""

import io
import os
import hashlib
import asyncio
import threading
import logging
import aiohttp

from pyrogram import Client, filters, enums
from pyrogram.types import (
    CallbackQuery,
    InputMediaPhoto,
    LinkPreviewOptions,
    Message,
)

# ─── LOAD .env ────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── CONFIG ──────────────────────────────────────────────────────────────────
from config import (
    API_ID, API_HASH, BOT_TOKEN,
    OWNER_ID, ADMIN_IDS,
    TMDB_API_KEY, TMDB_BASE, TMDB_IMG_BASE, TMDB_BG_BASE,
    SESSION_NAME, PLOT_MAX_CHARS, API_TIMEOUT, KEEP_ALIVE,
)

# ─── SCRIPT ──────────────────────────────────────────────────────────────────
from script import (
    START_TEXT, START_IMAGE, START_BUTTONS,
    HELP_TEXT, HELP_BUTTONS,
    ABOUT_TEXT, ABOUT_BUTTONS,
    SEARCHING_TEXT, NOT_FOUND_TEXT, API_ERROR_TEXT,
    USAGE_MOVIE_TEXT, USAGE_TV_TEXT, USAGE_SEARCH_TEXT,
    FSUB_JOINED, FSUB_STILL_NOT_JOINED,
    USAGE_ADDFSUB, USAGE_DELFSUB,
    build_caption, build_keyboard, build_fsub_message,
)

# ─── DATABASE ────────────────────────────────────────────────────────────────
from database import db

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)

# ─── KURIGRAM CLIENT ─────────────────────────────────────────────────────────
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=60,
    app_version="TMDB Poster Bot",
)


# ─── HELPERS ─────────────────────────────────────────────────────────────────
async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        return True
    return await db.is_admin(user_id)


async def is_banned(user_id: int) -> bool:
    if user_id == OWNER_ID or await is_admin(user_id):
        return False
    return await db.is_banned(user_id)


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def is_valid_image(data: bytes) -> bool:
    if not data or len(data) < 4:
        return False
    if data[:3] == b'\xff\xd8\xff':
        return True
    if data[:4] == b'\x89PNG':
        return True
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return True
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return True
    return False


def convert_to_jpeg(image_bytes: bytes) -> bytes:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()
    except Exception as e:
        log.warning("JPEG conversion failed: %s", e)
        return image_bytes


# ─── TMDB API ────────────────────────────────────────────────────────────────
async def tmdb_get(endpoint: str, params: dict) -> dict | None:
    """Generic TMDB API GET request."""
    params["api_key"] = TMDB_API_KEY
    params.setdefault("language", "en-US")
    url = f"{TMDB_BASE}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
    except Exception as e:
        log.error("TMDB API error [%s]: %s", endpoint, e)
    return None


async def fetch_movie(title: str, year: str = None) -> dict | None:
    """
    Search TMDB for a movie, then fetch full details (genres, runtime, imdb_id).
    Returns enriched dict or None.
    """
    params = {"query": title, "include_adult": "false"}
    if year:
        params["year"] = year

    data = await tmdb_get("/search/movie", params)
    if not data or not data.get("results"):
        return None

    movie = data["results"][0]
    movie_id = movie["id"]

    # Fetch full details for genres, runtime, imdb_id
    details = await tmdb_get(f"/movie/{movie_id}", {"append_to_response": "external_ids"})
    if details:
        details["media_type"] = "movie"
        details["imdb_id"] = (
            details.get("imdb_id")
            or details.get("external_ids", {}).get("imdb_id")
        )
        return details

    movie["media_type"] = "movie"
    return movie


async def fetch_tv(title: str, season: str = None) -> dict | None:
    """
    Search TMDB for a TV show, fetch full details.
    If season given, also fetch season-specific poster.
    """
    data = await tmdb_get("/search/tv", {"query": title})
    if not data or not data.get("results"):
        return None

    show = data["results"][0]
    show_id = show["id"]

    # Full show details
    details = await tmdb_get(
        f"/tv/{show_id}",
        {"append_to_response": "external_ids"}
    )
    if not details:
        show["media_type"] = "tv"
        return show

    details["media_type"] = "tv"
    details["imdb_id"] = details.get("external_ids", {}).get("imdb_id")

    # Season-specific poster
    if season:
        season_data = await tmdb_get(f"/tv/{show_id}/season/{season}", {})
        if season_data and season_data.get("poster_path"):
            details["season_poster_path"] = season_data["poster_path"]
            details["season_number"] = season
            details["season_name"] = season_data.get("name", f"Season {season}")
            details["overview"] = season_data.get("overview") or details.get("overview", "")

    return details


async def fetch_multi(title: str) -> dict | None:
    """
    Multi-search — returns first movie or TV result from TMDB.
    Fetches full details after finding the result.
    """
    data = await tmdb_get("/search/multi", {"query": title})
    if not data or not data.get("results"):
        return None

    # Pick first movie or tv result (skip persons)
    for result in data["results"]:
        if result.get("media_type") in ("movie", "tv"):
            if result["media_type"] == "movie":
                return await fetch_movie(result.get("title", title))
            else:
                return await fetch_tv(result.get("name", title))
    return None


def get_poster_url(data: dict) -> str | None:
    """Return the best available poster URL from a TMDB result."""
    # Season-specific poster takes priority for TV seasons
    path = (
        data.get("season_poster_path")
        or data.get("poster_path")
        or data.get("backdrop_path")
    )
    if not path:
        return None
    # Use backdrop base for backdrop, poster base for posters
    if data.get("season_poster_path") == path or data.get("poster_path") == path:
        return f"{TMDB_IMG_BASE}{path}"
    return f"{TMDB_BG_BASE}{path}"


# ─── IMAGE DOWNLOADER ────────────────────────────────────────────────────────
async def download_image(url: str) -> bytes | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                resp.raise_for_status()
                return await resp.read()
    except Exception as e:
        log.error("Image download failed: %s", e)
    return None


# ─── CORE POSTER SENDER ──────────────────────────────────────────────────────
async def send_poster(
    client: Client,
    message: Message,
    data: dict,
    image_url: str,
):
    caption  = build_caption(data, plot_max=PLOT_MAX_CHARS)
    keyboard = build_keyboard(data)
    cache_key = url_hash(image_url)

    # ── 1. Check cache ────────────────────────────────────────────────────
    cached = await db.get_cached_image(cache_key)

    if cached and cached.get("file_id"):
        log.info("Cache HIT (file_id): %s", cache_key)
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=cached["file_id"],
                caption=caption,
                reply_markup=keyboard,
            )
            return
        except Exception as e:
            log.warning("Cached file_id failed: %s", e)
            await db.update_file_id(cache_key, None)

    if cached and cached.get("bytes"):
        image_bytes = bytes(cached["bytes"])
        log.info("Cache HIT (bytes): %s", cache_key)
        if not is_valid_image(image_bytes):
            await db.clear_cache(cache_key)
            image_bytes = None
    else:
        image_bytes = None

    # ── 2. Download if needed ─────────────────────────────────────────────
    if not image_bytes:
        log.info("Downloading: %s", image_url)
        image_bytes = await download_image(image_url)

        if not image_bytes or not is_valid_image(image_bytes):
            log.error("Invalid image from TMDB CDN")
            await message.reply(
                f"{caption}\n\n🖼 [View Poster]({image_url})",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=keyboard,
            )
            return

        image_bytes = convert_to_jpeg(image_bytes)
        await db.cache_image(cache_key, image_url, image_bytes=image_bytes)

    # ── 3. Send photo ─────────────────────────────────────────────────────
    try:
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=io.BytesIO(image_bytes),
            caption=caption,
            reply_markup=keyboard,
        )
        if sent and sent.photo:
            await db.update_file_id(cache_key, sent.photo.file_id)
        return
    except Exception as e:
        log.warning("send_photo failed: %s — trying document", e)

    # ── 4. Fallback: send as document ─────────────────────────────────────
    try:
        sent = await client.send_document(
            chat_id=message.chat.id,
            document=io.BytesIO(image_bytes),
            file_name="poster.jpg",
            caption=caption,
            reply_markup=keyboard,
        )
        if sent and sent.document:
            await db.update_file_id(cache_key, sent.document.file_id)
        return
    except Exception as e:
        log.error("send_document failed: %s", e)

    # ── 5. Last resort: plain link ────────────────────────────────────────
    await message.reply(
        f"{caption}\n\n🖼 [View Poster]({image_url})",
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ─── FORCE SUBSCRIBE ─────────────────────────────────────────────────────────
async def check_fsub(client: Client, user_id: int) -> tuple[bool, list[dict]]:
    channel_ids = await db.get_fsub_channels()
    if not channel_ids:
        return True, []

    not_joined = []
    for ch_id in channel_ids:
        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status.value in ("left", "banned", "restricted"):
                raise Exception("not member")
        except Exception:
            try:
                chat = await client.get_chat(ch_id)
                invite = await client.export_chat_invite_link(ch_id)
                not_joined.append({"id": ch_id, "title": chat.title, "invite_link": invite})
            except Exception as e:
                log.warning("Fsub channel error %s: %s", ch_id, e)

    return len(not_joined) == 0, not_joined


# ════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════════

@app.on_message(filters.private & filters.incoming, group=-1)
async def middleware(client: Client, message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)

    if await is_banned(user_id):
        await message.reply("🚫 You are banned from using this bot.")
        message.stop_propagation()
        return

    cmd = message.command[0].lower() if message.command else ""
    if await is_admin(user_id) or cmd == "start":
        return

    joined, missing = await check_fsub(client, user_id)
    if not joined:
        text, keyboard = build_fsub_message(missing)
        await message.reply(text, reply_markup=keyboard)
        message.stop_propagation()


# ════════════════════════════════════════════════════════════════════════════
# USER COMMANDS
# ════════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, message: Message):
    first_name = message.from_user.first_name or "there"
    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=START_IMAGE,
            caption=START_TEXT.format(first_name=first_name),
            reply_markup=START_BUTTONS,
        )
    except Exception:
        await message.reply(
            START_TEXT.format(first_name=first_name),
            reply_markup=START_BUTTONS,
        )


@app.on_message(filters.command("help") & filters.private)
async def cmd_help(client: Client, message: Message):
    await message.reply(HELP_TEXT, reply_markup=HELP_BUTTONS)


@app.on_message(filters.command("about") & filters.private)
async def cmd_about(client: Client, message: Message):
    me = await client.get_me()
    await message.reply(
        ABOUT_TEXT.format(me.first_name),
        reply_markup=ABOUT_BUTTONS,
        parse_mode=enums.ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@app.on_message(filters.command("movie") & filters.private)
async def cmd_movie(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_MOVIE_TEXT)

    if len(args) > 1 and args[-1].isdigit() and len(args[-1]) == 4:
        title, year = " ".join(args[:-1]), args[-1]
    else:
        title, year = " ".join(args), None

    thinking = await message.reply(SEARCHING_TEXT.format(title=title))
    data = await fetch_movie(title, year)
    await thinking.delete()

    if not data:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    image_url = get_poster_url(data)
    if not image_url:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    await send_poster(client, message, data, image_url)


@app.on_message(filters.command("tv") & filters.private)
async def cmd_tv(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_TV_TEXT)

    if len(args) > 1 and args[-1].isdigit():
        title, season = " ".join(args[:-1]), args[-1]
    else:
        title, season = " ".join(args), None

    thinking = await message.reply(SEARCHING_TEXT.format(title=title))
    data = await fetch_tv(title, season)
    await thinking.delete()

    if not data:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    image_url = get_poster_url(data)
    if not image_url:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    await send_poster(client, message, data, image_url)


@app.on_message(filters.command("search") & filters.private)
async def cmd_search(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_SEARCH_TEXT)

    title = " ".join(args)
    thinking = await message.reply(SEARCHING_TEXT.format(title=title))
    data = await fetch_multi(title)
    await thinking.delete()

    if not data:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    image_url = get_poster_url(data)
    if not image_url:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    await send_poster(client, message, data, image_url)


@app.on_message(
    filters.private & filters.text
    & ~filters.command([
        "start", "help", "about", "movie", "tv", "search",
        "stats", "admins", "ban", "unban", "banned", "broadcast",
        "addfsub", "delfsub", "listfsub", "addadmin", "deladmin",
    ])
)
async def plain_search(client: Client, message: Message):
    title = message.text.strip()
    if not title:
        return

    thinking = await message.reply(SEARCHING_TEXT.format(title=title))
    data = await fetch_multi(title)
    await thinking.delete()

    if not data:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    image_url = get_poster_url(data)
    if not image_url:
        return await message.reply(NOT_FOUND_TEXT.format(title=title))

    await send_poster(client, message, data, image_url)


# ════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("stats") & filters.private)
async def cmd_stats(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    total  = await db.total_users()
    banned = len(await db.get_banned_users())
    admins = await db.get_all_admins()
    await message.reply(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: `{total}`\n"
        f"🚫 Banned Users: `{banned}`\n"
        f"👮 DB Admins: `{len(admins)}`\n"
        f"🔑 Static Admins: `{len(ADMIN_IDS)}`"
    )


@app.on_message(filters.command("admins") & filters.private)
async def cmd_admins(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    db_admins  = await db.get_all_admins()
    all_admins = list(set([OWNER_ID] + ADMIN_IDS + db_admins))
    lines = ["👮 **Admin List**\n"]
    for uid in all_admins:
        tag = " 👑 Owner" if uid == OWNER_ID else ""
        lines.append(f"• `{uid}`{tag}")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("addadmin") & filters.private)
async def cmd_addadmin(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ Owner only.")
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/addadmin <user_id>`")
    user_id = int(args[0])
    if user_id == OWNER_ID:
        return await message.reply("That's already the owner.")
    await db.add_admin(user_id)
    await message.reply(f"✅ `{user_id}` added as admin.")


@app.on_message(filters.command("deladmin") & filters.private)
async def cmd_deladmin(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ Owner only.")
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/deladmin <user_id>`")
    user_id = int(args[0])
    if user_id == OWNER_ID:
        return await message.reply("Cannot remove the owner.")
    await db.del_admin(user_id)
    await message.reply(f"✅ `{user_id}` removed from admins.")


@app.on_message(filters.command("ban") & filters.private)
async def cmd_ban(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/ban <user_id>`")
    user_id = int(args[0])
    if user_id == OWNER_ID or await is_admin(user_id):
        return await message.reply("Cannot ban an admin or owner.")
    await db.ban_user(user_id)
    await message.reply(f"🚫 `{user_id}` has been banned.")


@app.on_message(filters.command("unban") & filters.private)
async def cmd_unban(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/unban <user_id>`")
    await db.unban_user(int(args[0]))
    await message.reply(f"✅ `{args[0]}` has been unbanned.")


@app.on_message(filters.command("banned") & filters.private)
async def cmd_banned(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    banned = await db.get_banned_users()
    if not banned:
        return await message.reply("✅ No banned users.")
    lines = ["🚫 **Banned Users**\n"] + [f"• `{uid}`" for uid in banned]
    await message.reply("\n".join(lines))


@app.on_message(filters.command("broadcast") & filters.private)
async def cmd_broadcast(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    if not message.reply_to_message:
        return await message.reply("Reply to a message with `/broadcast`.")
    status = await message.reply("📢 Broadcasting…")
    users  = await db.get_all_users()
    done, failed = 0, 0
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            done += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await status.edit(
        f"📢 **Broadcast Complete**\n\n"
        f"✅ Sent: `{done}`\n"
        f"❌ Failed: `{failed}`\n"
        f"👥 Total: `{len(users)}`"
    )


@app.on_message(filters.command("addfsub") & filters.private)
async def cmd_addfsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_ADDFSUB)
    raw = args[0].lstrip("-")
    if not raw.isdigit():
        return await message.reply("❌ Invalid channel ID.")
    channel_id = int(args[0])
    try:
        chat = await client.get_chat(channel_id)
        bot_member = await client.get_chat_member(channel_id, "me")
        if bot_member.status.value not in ("administrator", "creator"):
            return await message.reply(
                "❌ Bot is not an admin in that channel.\n"
                "Make the bot admin with **Invite Users** permission."
            )
    except Exception as e:
        return await message.reply(f"❌ Could not access channel: `{e}`")
    await db.add_fsub_channel(channel_id)
    await message.reply(
        f"✅ **{chat.title}** added to force subscribe list.\n"
        f"Channel ID: `{channel_id}`"
    )


@app.on_message(filters.command("delfsub") & filters.private)
async def cmd_delfsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_DELFSUB)
    raw = args[0].lstrip("-")
    if not raw.isdigit():
        return await message.reply("❌ Invalid channel ID.")
    channel_id = int(args[0])
    if not await db.fsub_channel_exists(channel_id):
        return await message.reply("❌ That channel is not in the fsub list.")
    await db.remove_fsub_channel(channel_id)
    await message.reply(f"✅ Channel `{channel_id}` removed from force subscribe list.")


@app.on_message(filters.command("listfsub") & filters.private)
async def cmd_listfsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")
    channels = await db.get_fsub_channels()
    if not channels:
        return await message.reply("📭 No force subscribe channels set.")
    lines = ["📋 **Force Subscribe Channels**\n"]
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            lines.append(f"• **{chat.title}** — `{ch_id}`")
        except Exception:
            lines.append(f"• `{ch_id}` _(could not fetch name)_")
    await message.reply("\n".join(lines))


# ════════════════════════════════════════════════════════════════════════════
# CALLBACK QUERY HANDLERS
# ════════════════════════════════════════════════════════════════════════════

@app.on_callback_query(filters.regex("^check_fsub$"))
async def cb_check_fsub(client: Client, query: CallbackQuery):
    joined, missing = await check_fsub(client, query.from_user.id)
    if joined:
        await query.edit_message_text(FSUB_JOINED)
        await query.answer("✅ Verified!", show_alert=False)
    else:
        text, keyboard = build_fsub_message(missing)
        await query.edit_message_text(text, reply_markup=keyboard)
        await query.answer(FSUB_STILL_NOT_JOINED, show_alert=True)


@app.on_callback_query(filters.regex("^start$"))
async def cb_start(client: Client, query: CallbackQuery):
    first_name = query.from_user.first_name or "there"
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=START_IMAGE,
                caption=START_TEXT.format(first_name=first_name),
            ),
            reply_markup=START_BUTTONS,
        )
    except Exception:
        await query.edit_message_text(
            START_TEXT.format(first_name=first_name),
            reply_markup=START_BUTTONS,
        )
    await query.answer()


@app.on_callback_query(filters.regex("^help$"))
async def cb_help(client: Client, query: CallbackQuery):
    await query.edit_message_text(HELP_TEXT, reply_markup=HELP_BUTTONS)
    await query.answer()


@app.on_callback_query(filters.regex("^about$"))
async def cb_about(client: Client, query: CallbackQuery):
    me = await client.get_me()
    await query.edit_message_text(
        ABOUT_TEXT.format(me.first_name),
        reply_markup=ABOUT_BUTTONS,
        parse_mode=enums.ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await query.answer()


# ─── KOYEB HEALTH SERVER ─────────────────────────────────────────────────────
from flask import Flask as _Flask

_health_app = _Flask(__name__)

@_health_app.route("/")
def _home():
    return "TMDB Poster Bot is running! 🎬", 200

@_health_app.route("/health")
def _health():
    return {"status": "ok"}, 200

def _run_health_server():
    port = int(os.getenv("PORT", "8000"))
    log.info("Health server on port %s", port)
    _health_app.run(host="0.0.0.0", port=port, use_reloader=False)


# ─── RUN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    async def on_start(client):
        ok = await db.ping()
        if ok:
            log.info("MongoDB connected successfully")
        else:
            log.critical("MongoDB connection FAILED — check DB_URI env var")

    app.on_connect()(on_start)

    if KEEP_ALIVE:
        threading.Thread(target=_run_health_server, daemon=True).start()

    log.info("Starting TMDB Poster Bot…")
    app.run()
