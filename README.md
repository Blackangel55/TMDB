# 🎬 TMDB Poster Bot

A Telegram bot that fetches **movie & TV show posters** with full details — ratings, genres, overview, runtime and more — powered by **The Movie Database (TMDB) API**.

---

## ✨ Features

- 🎬 Movie posters with rating, genres, runtime, overview
- 📺 TV show & season-specific posters
- 🔍 Auto-detect movie or TV show from plain text
- 🖼 Image caching in MongoDB — instant repeat searches
- 🔒 Force Subscribe — users must join channels before using
- 👮 Admin system — ban, unban, broadcast, manage admins
- 🚀 Koyeb / Docker / Railway ready with health check server

---

## 📁 Project Structure

```
tmdb_poster_bot/
├── bot.py               ← Main bot (handlers, API, image sender)
├── script.py            ← All messages, captions, keyboards
├── config.py            ← All settings loaded from env vars
├── database/
│   ├── __init__.py
│   └── database.py      ← MongoDB handler (users, cache, fsub, ban)
├── requirements.txt
├── runtime.txt          ← python-3.12.3
├── Procfile             ← web: python bot.py
├── Dockerfile
├── .env.example
└── README.md
```

---

## ⚙️ Requirements

- Python 3.12+
- Telegram **API_ID** & **API_HASH** → https://my.telegram.org
- **Bot Token** → [@BotFather](https://t.me/BotFather)
- **TMDB API Key** → https://www.themoviedb.org/settings/api _(free, instant)_
- **MongoDB URI** → https://cloud.mongodb.com _(free tier works)_

---

## 🚀 Quick Start

```bash
# 1. Clone / download the project
git clone https://github.com/youruser/tmdb-poster-bot.git
cd tmdb-poster-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your values

# 4. Run
python bot.py
```

---

## 🔧 Environment Variables

Set these in your `.env` file or directly in your cloud dashboard.

### Required

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from https://my.telegram.org |
| `API_HASH` | Telegram API Hash from https://my.telegram.org |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Your Telegram user ID (get from [@userinfobot](https://t.me/userinfobot)) |
| `DB_URI` | MongoDB connection string |
| `TMDB_API_KEY` | TMDB API key from https://www.themoviedb.org/settings/api |

### Optional

| Variable | Default | Description |
|---|---|---|
| `ADMIN_IDS` | _(empty)_ | Comma-separated static admin user IDs |
| `DB_NAME` | `tmdb_poster_bot` | MongoDB database name |
| `SESSION_NAME` | `/app/sessions/tmdb_poster_bot` | Kurigram session file path |
| `PLOT_MAX_CHARS` | `300` | Max characters for overview in caption |
| `API_TIMEOUT` | `15` | TMDB API request timeout in seconds |
| `KEEP_ALIVE` | `true` | Run Flask health server (required for Koyeb) |
| `PORT` | `8000` | Health server port |

---

## 👤 User Commands

| Command | Example | Description |
|---|---|---|
| `/start` | `/start` | Welcome message with image |
| `/help` | `/help` | Full help & tips |
| `/about` | `/about` | About this bot |
| `/movie Title [Year]` | `/movie RRR 2022` | Fetch a movie poster |
| `/tv Title [Season]` | `/tv Asur 2` | Fetch a TV season poster |
| `/search Title` | `/search Mirzapur` | Auto-detect movie or series |
| Just type a title | `KGF Chapter 2` | Quick search |

---

## 👮 Admin Commands

> Admins can be added dynamically or set statically via `ADMIN_IDS`.

| Command | Example | Description |
|---|---|---|
| `/stats` | `/stats` | Total users, banned count, admin count |
| `/admins` | `/admins` | List all admins |
| `/ban <user_id>` | `/ban 123456789` | Ban a user |
| `/unban <user_id>` | `/unban 123456789` | Unban a user |
| `/banned` | `/banned` | List all banned users |
| `/broadcast` | _(reply to msg)_ `/broadcast` | Send message to all users |
| `/addfsub <channel_id>` | `/addfsub -1001234567890` | Add force subscribe channel |
| `/delfsub <channel_id>` | `/delfsub -1001234567890` | Remove force subscribe channel |
| `/listfsub` | `/listfsub` | List all force subscribe channels |

---

## 👑 Owner-Only Commands

> Owner is set via `OWNER_ID`. Cannot be banned or demoted.

| Command | Example | Description |
|---|---|---|
| `/addadmin <user_id>` | `/addadmin 123456789` | Promote a user to admin |
| `/deladmin <user_id>` | `/deladmin 123456789` | Remove a user from admins |

---

## 📡 Force Subscribe Setup

1. Add bot as **admin** in your channel with **Invite Users via Link** permission
2. Get the channel ID (forward a message to [@userinfobot](https://t.me/userinfobot))
3. Send `/addfsub -1001234567890` in the bot
4. Done — users must join before using the bot

> Admins and owner always bypass the force subscribe check.

---

## 🐳 Docker

```bash
# Build
docker build -t tmdb-poster-bot .

# Run
docker run -d \
  -e API_ID=12345678 \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e OWNER_ID=your_user_id \
  -e DB_URI=mongodb+srv://... \
  -e TMDB_API_KEY=your_tmdb_key \
  tmdb-poster-bot
```

Or with Docker Compose:

```bash
cp .env.example .env   # fill in your values
docker compose up -d
docker compose logs -f
```

---

## ☁️ Deploy on Koyeb

1. Push code to GitHub
2. Koyeb dashboard → **Create Service** → GitHub → your repo
3. Build method: **Dockerfile**
4. Port: `8000` | Protocol: `HTTP` | Health check: `/health`
5. Add env vars in the **Environment variables** section
6. Click **Deploy**

### Koyeb env vars to set

| Key | Value |
|---|---|
| `API_ID` | your value |
| `API_HASH` | ✅ mark as secret |
| `BOT_TOKEN` | ✅ mark as secret |
| `OWNER_ID` | your Telegram user ID |
| `DB_URI` | ✅ mark as secret |
| `TMDB_API_KEY` | ✅ mark as secret |
| `KEEP_ALIVE` | `true` |
| `PORT` | `8000` |

> **MongoDB Atlas:** Make sure to whitelist `0.0.0.0/0` under Network Access so Koyeb can connect.

---

## 🖼 Customise Start Image

Edit `script.py`:

```python
START_IMAGE = "https://your-image-url.jpg"
# or use a Telegram file_id after uploading once
```

---

## 📝 Commands


```
start - Welcome message
help - Full help & tips
about - About this bot
movie - Fetch a movie poster
tv - Fetch a TV season poster
search - Auto-detect movie or series
```

---


## 📄 License

MIT — free to use, modify and deploy.
