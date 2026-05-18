import os

# ─── TELEGRAM ────────────────────────────────────────────────────────────────
API_ID    = int(os.getenv("API_ID", "0"))
API_HASH  = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# ─── OWNER / ADMIN ───────────────────────────────────────────────────────────
OWNER_ID  = int(os.getenv("OWNER_ID", "0"))

_ADMIN_IDS   = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = (
    [int(x.strip()) for x in _ADMIN_IDS.split(",") if x.strip().isdigit()]
    if _ADMIN_IDS else []
)

# ─── MONGODB ─────────────────────────────────────────────────────────────────
DB_URI  = os.getenv("DB_URI", "")
DB_NAME = os.getenv("DB_NAME", "tmdb_poster")

# ─── TMDB API ────────────────────────────────────────────────────────────────
# Get your free API key at https://www.themoviedb.org/settings/api
TMDB_API_KEY  = os.getenv("TMDB_API_KEY", "YOUR_TMDB_API_KEY")
TMDB_BASE     = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w780"   # poster size
TMDB_BG_BASE  = "https://image.tmdb.org/t/p/w1280"  # backdrop size

# ─── BOT SETTINGS ────────────────────────────────────────────────────────────
SESSION_NAME   = os.getenv("SESSION_NAME", "/app/sessions/tmdb_poster_bot")
PLOT_MAX_CHARS = int(os.getenv("PLOT_MAX_CHARS", "300"))
API_TIMEOUT    = int(os.getenv("API_TIMEOUT", "15"))
KEEP_ALIVE     = os.getenv("KEEP_ALIVE", "true").lower() == "true"
