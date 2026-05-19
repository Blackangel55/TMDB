from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ════════════════════════════════════════════════════════════════════════════
# START IMAGE — replace with your image URL or Telegram file_id
# ════════════════════════════════════════════════════════════════════════════

START_IMAGE = "https://i.ibb.co/ZpbyxgPM/x.jpg"  # ← replace this


# ════════════════════════════════════════════════════════════════════════════
# START MESSAGE
# ════════════════════════════════════════════════════════════════════════════

START_TEXT = """🎬 **Welcome to TMDB Poster Bot!**

Hey {first_name}! 👋
I fetch **movie & TV show posters** with full details from TMDB.

Just **type any movie or show name** to get its poster!

_Example:_ `RRR`
_Example:_ `Mirzapur`
_Example:_ `The Dark Knight`

💡 `/help` — Full help & tips
ℹ️ `/about` — About this bot
"""

START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("💡 Help", callback_data="help"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
    ],
])


# ════════════════════════════════════════════════════════════════════════════
# HELP MESSAGE
# ════════════════════════════════════════════════════════════════════════════

HELP_TEXT = """💡 **TMDB Poster Bot — Help**

━━━━━━━━━━━━━━━━━━━━
⚡ **Quick Search — Just Type!**
━━━━━━━━━━━━━━━━━━━━
Just **type any movie or show name** directly.
No command needed — the bot auto-detects.

• `RRR`
• `Mirzapur`
• `KGF Chapter 2`
• `The Dark Knight`
• `Scam 1992`

━━━━━━━━━━━━━━━━━━━━
🎬 **Movie — Specific Search**
━━━━━━━━━━━━━━━━━━━━
Use when you want to filter by year:

`/movie Title Year`

• `/movie RRR 2022`
• `/movie Bahubali 2015`
• `/movie The Dark Knight 2008`

━━━━━━━━━━━━━━━━━━━━
📺 **TV / OTT — Season Poster**
━━━━━━━━━━━━━━━━━━━━
Use when you want a specific season poster:

`/tv Title Season`

• `/tv Asur 2`
• `/tv Sacred Games 1`
• `/tv Mirzapur 3`

━━━━━━━━━━━━━━━━━━━━
💬 **Tips**
• Typing the name is the fastest way to search
• Use `/movie` with year if wrong result appears
• Use `/tv` with season for season-specific poster
• Posters include ⭐ rating, 🏷 genres, 📝 overview
"""

HELP_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Back to Start", callback_data="start")],
])


# ════════════════════════════════════════════════════════════════════════════
# ABOUT MESSAGE
# ════════════════════════════════════════════════════════════════════════════

ABOUT_TEXT = """<b>○ 𝖬𝗒 𝖭𝖺𝗆𝖾 : {}</b>
<b>○ 𝖢𝗋𝖾𝖺𝗍𝗈𝗋 : <a href='https://t.me/GUARDIANff'>𝖳𝗁𝗂𝗌 𝖯𝖾𝗋𝗌𝗈𝗇</a></b>
<b>○ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 : 𝖯𝗒𝗍𝗁𝗈𝗇 𝟥</b>
<b>○ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖦𝗋𝗈𝗎𝗉 : <a href='https://t.me/AM_FILMS'>𝖳𝖺𝗉 𝖧𝖾𝗋𝖾</a></b>"""

ABOUT_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Back to Start", callback_data="start")],
])


# ════════════════════════════════════════════════════════════════════════════
# STATUS MESSAGES
# ════════════════════════════════════════════════════════════════════════════

SEARCHING_TEXT = "🔍 Searching for **{title}**…"

NOT_FOUND_TEXT = """❌ **No results found for:** `{title}`

Try:
• Check the spelling
• Add year: `/movie {title} 2023`
• For a series: `/tv {title}`
"""

API_ERROR_TEXT = """⚠️ **Could not reach TMDB API.**

Please try again in a moment.
"""

USAGE_MOVIE_TEXT = """ℹ️ **Usage:** `/movie Title [Year]`

• `/movie RRR 2022`
• `/movie Bahubali`
"""

USAGE_TV_TEXT = """ℹ️ **Usage:** `/tv Title [Season]`

• `/tv Asur 2`
• `/tv Mirzapur`
"""




# ════════════════════════════════════════════════════════════════════════════
# FORCE SUBSCRIBE
# ════════════════════════════════════════════════════════════════════════════

def build_fsub_message(channels: list[dict]) -> tuple[str, InlineKeyboardMarkup]:
    text = "👋 **Hello!**\n\nTo use this bot you must join our channel(s) first:\n\n"
    for i, ch in enumerate(channels, 1):
        text += f"{i}. **{ch['title']}**\n"
    text += "\nAfter joining, tap **✅ I've Joined** below."

    buttons = [[InlineKeyboardButton(f"➕ Join {ch['title']}", url=ch["invite_link"])]
               for ch in channels]
    buttons.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_fsub")])
    return text, InlineKeyboardMarkup(buttons)


FSUB_STILL_NOT_JOINED = (
    "❌ You haven't joined all required channels yet!\n\n"
    "Please join all channels and tap **✅ I've Joined** again."
)
FSUB_JOINED   = "✅ **Verified!** Welcome, enjoy the bot 🎬"
USAGE_ADDFSUB = "Usage: `/addfsub <channel_id>`\nExample: `/addfsub -1001234567890`"
USAGE_DELFSUB = "Usage: `/delfsub <channel_id>`\nExample: `/delfsub -1001234567890`"


# ════════════════════════════════════════════════════════════════════════════
# CAPTION BUILDER  (TMDB fields)
# ════════════════════════════════════════════════════════════════════════════

def build_simple_caption(data: dict) -> str:
    """Minimal caption — just title and year. Shown on first poster send."""
    title = data.get("title") or data.get("name", "Unknown")
    date  = data.get("release_date") or data.get("first_air_date", "")
    year  = date[:4] if date else ""
    media = data.get("media_type", "")
    icon  = "📺" if media == "tv" or data.get("number_of_seasons") else "🎬"
    return f"<b>{icon} {title} [{year}]</b>" if year else f"<b>{icon} {title}</b>"


def build_caption(data: dict, plot_max: int = 300) -> str:
    """
    Build HTML caption from TMDB response.
    Works for both movie and TV results.
    """
    title    = data.get("title") or data.get("name", "Unknown")
    date     = data.get("release_date") or data.get("first_air_date", "")
    year     = date[:4] if date else ""
    rating   = data.get("vote_average", "")
    overview = data.get("overview", "")
    genres   = data.get("genres", [])
    runtime  = data.get("runtime", "")
    seasons  = data.get("number_of_seasons", "")
    episodes = data.get("number_of_episodes", "")
    languages = data.get("spoken_languages", [])
    countries = data.get("production_countries", [])
    cast_list = data.get("cast", [])             # populated by fetch functions
    season_name = data.get("season_name", "")
    season_num  = data.get("season_number", "")

    # ── Title + year ──
    title_line = f"{title} [{year}]" if year else title
    if season_name:
        title_line += f" | {season_name}"

    # ── Duration ──
    if runtime:
        duration = f"{runtime} min"
    elif seasons:
        s = int(seasons)
        duration = f"{s} Season{'s' if s > 1 else ''}"
        if episodes:
            duration += f" · {episodes} Episodes"
    else:
        duration = "N/A"

    # ── Release info ──
    release_info = date if date else "N/A"

    # ── Rating ──
    rating_str = f"{round(float(rating), 1)}/10 ⭐" if rating else "N/A"

    # ── Language ──
    if languages:
        lang_str = ", ".join(
            l.get("english_name") or l.get("name", "") for l in languages[:3]
        )
    else:
        lang_str = "N/A"

    # ── Country ──
    if countries:
        country_str = ", ".join(c.get("name", "") for c in countries[:3])
    else:
        country_str = "N/A"

    # ── Genre ──
    genre_str = ", ".join(g["name"] for g in genres[:5]) if genres else "N/A"

    # ── Plot ──
    if overview:
        plot_str = (overview[:plot_max] + "…") if len(overview) > plot_max else overview
    else:
        plot_str = "N/A"

    # ── Cast ──
    if cast_list:
        cast_str = ", ".join(cast_list[:5])
    else:
        cast_str = "N/A"

    caption = (
        f"<b>🎬𝚃𝚒𝚝𝚕𝚎 :- {title_line}\n\n"
        f"⭐️𝚁𝚊𝚝𝚒𝚗𝚐 :- {rating_str}\n\n"
        f"⏱️𝙳𝚞𝚛𝚊𝚝𝚒𝚘𝚗 :- <i>{duration}</i>\n\n"
        f"🎞️𝚁𝚎𝚕𝚎𝚊𝚜𝚎 𝚒𝚗𝚏𝚘 :- {release_info}\n\n"
        f"🔊𝙻𝚊𝚗𝚐𝚞𝚊𝚐𝚎 :- {lang_str}\n\n"
        f"🏳️𝙲𝚘𝚞𝚗𝚝𝚛𝚢 𝙾𝚏 𝙾𝚛𝚒𝚐𝚒𝚗 :- {country_str}\n\n"
        f"🔖𝙶𝚎𝚗𝚛𝚎 :- {genre_str}\n\n"
        f"📋𝙿𝚕𝚘𝚝 𝚘𝚏 𝚝𝚑𝚎 𝚖𝚘𝚟𝚒𝚎 :- {plot_str}\n\n"
        f"📽️𝙲𝚊𝚜𝚝 𝚒𝚗𝚏𝚘 :- {cast_str}</b>"
    )

    return caption


def build_keyboard(data: dict, show_details: bool = True) -> InlineKeyboardMarkup | None:
    """
    Build inline keyboard.
    Row 1: 📋 Details button (callback) — tapping shows full caption
    Row 2: IMDb + TMDB url buttons
    """
    tmdb_id = data.get("id")
    imdb_id = data.get("imdb_id")
    media   = data.get("media_type", "movie")
    kind    = "tv" if (media == "tv" or data.get("number_of_seasons")) else "movie"

    rows = []

    # Details button — callback_data encodes tmdb_id and media type
    if show_details and tmdb_id:
        rows.append([
            InlineKeyboardButton(
                "📋 Details",
                callback_data=f"details_{kind}_{tmdb_id}"
            )
        ])

    # URL buttons
    url_row = []
    if imdb_id:
        url_row.append(InlineKeyboardButton("🎞 IMDb", url=f"https://www.imdb.com/title/{imdb_id}"))
    if tmdb_id:
        url_row.append(InlineKeyboardButton(
            "🎬 TMDB", url=f"https://www.themoviedb.org/{kind}/{tmdb_id}"
        ))
    if url_row:
        rows.append(url_row)

    return InlineKeyboardMarkup(rows) if rows else None


def build_details_keyboard(data: dict) -> InlineKeyboardMarkup | None:
    """Keyboard shown after details are expanded — no Details button, only links."""
    return build_keyboard(data, show_details=False)
