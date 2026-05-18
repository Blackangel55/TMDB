from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ════════════════════════════════════════════════════════════════════════════
# START IMAGE — replace with your image URL or Telegram file_id
# ════════════════════════════════════════════════════════════════════════════

START_IMAGE = "https://i.ibb.co/your-image.jpg"  # ← replace this


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
<b>○ 𝖯𝗈𝗌𝗍𝖾𝗋 𝖠𝖯𝖨 : 𝖳𝖬𝖣𝖡</b>
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

def build_caption(data: dict, plot_max: int = 300) -> str:
    """
    Build caption from TMDB response.
    Works for both movie and TV (multi search) results.
    TMDB fields:
      title / name, release_date / first_air_date,
      vote_average, genres, overview, media_type,
      number_of_seasons (TV details)
    """
    title    = data.get("title") or data.get("name", "Unknown")
    date     = data.get("release_date") or data.get("first_air_date", "")
    year     = date[:4] if date else ""
    rating   = data.get("vote_average", "")
    overview = data.get("overview", "")
    genres   = data.get("genres", [])           # list of {id, name}
    seasons  = data.get("number_of_seasons", "")
    runtime  = data.get("runtime", "")          # movie only
    media    = data.get("media_type", "")       # from multi search

    icon = "📺" if media == "tv" or seasons else "🎬"

    lines = []
    if year:
        lines.append(f"{icon} **{title}** ({year})")
    else:
        lines.append(f"{icon} **{title}**")

    lines.append("━━━━━━━━━━━━━━━━━━━━")

    meta = []
    if rating:
        meta.append(f"⭐ {round(float(rating), 1)}/10")
    if runtime:
        meta.append(f"🕐 {runtime} min")
    if seasons:
        meta.append(f"📺 {seasons} Season{'s' if int(seasons) > 1 else ''}")
    if meta:
        lines.append("  |  ".join(meta))

    if genres:
        lines.append("🏷 " + " · ".join(g["name"] for g in genres[:4]))

    if overview:
        short = (overview[:plot_max] + "…") if len(overview) > plot_max else overview
        lines.append(f"\n📝 _{short}_")

    return "\n".join(lines)


def build_keyboard(data: dict) -> InlineKeyboardMarkup | None:
    """Build IMDb / TMDB buttons if IDs are available."""
    buttons = []
    imdb_id = data.get("imdb_id")
    tmdb_id = data.get("id")
    media   = data.get("media_type", "movie")

    if imdb_id:
        buttons.append(InlineKeyboardButton("🎞 IMDb", url=f"https://www.imdb.com/title/{imdb_id}"))
    if tmdb_id:
        kind = "tv" if (media == "tv" or data.get("number_of_seasons")) else "movie"
        buttons.append(InlineKeyboardButton(
            "🎬 TMDB", url=f"https://www.themoviedb.org/{kind}/{tmdb_id}"
        ))

    return InlineKeyboardMarkup([buttons]) if buttons else None
