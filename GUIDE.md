# 🤖 Discord Auto-Translate Bot — Full Guide

## 📁 Files
- `bot.py` — the bot code
- `requirements.txt` — Python dependencies
- `channel_config.json` — auto-created when you configure channels

---

## ✅ STEP 1 — Create Your Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **"New Application"** → give it a name (e.g. TranslateBot)
3. Click **"Bot"** in the left sidebar
4. Click **"Reset Token"** → copy the token
5. Open `bot.py` and replace:
   ```
   TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
   with your actual token.

6. Under **"Privileged Gateway Intents"**, enable:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (optional)

---

## ✅ STEP 2 — Invite Bot to Your Server

1. Go to **OAuth2 → URL Generator** in the Dev Portal
2. Under **Scopes**, check: `bot` and `applications.commands`
3. Under **Bot Permissions**, check:
   - Read Messages / View Channels
   - Send Messages
   - Embed Links
   - Read Message History
4. Copy the generated URL → open in browser → select your server → click **Authorize**

---

## ✅ STEP 3 — Run Locally (for testing)

```bash
# Install Python 3.10+ first from https://python.org

pip install -r requirements.txt
python bot.py
```

You should see:
```
✅ Logged in as TranslateBot#1234
✅ Synced 5 slash commands
```

---

## ✅ STEP 4 — Use the Bot in Discord

### Setup translation for a channel:
```
/translate_setup  from_lang: ru  to_lang: en
/translate_setup  from_lang: en  to_lang: ru
```

### Enable/disable:
```
/translate_on
/translate_off
```

### Check current settings:
```
/translate_status
```

### Translate one message manually:
```
/translate_once  text: Привет мир  to_lang: en
```

### Remove a pair:
```
/translate_remove  from_lang: ru  to_lang: en
```

### Common Language Codes:
| Language   | Code  |
|------------|-------|
| English    | en    |
| Russian    | ru    |
| German     | de    |
| French     | fr    |
| Spanish    | es    |
| Chinese    | zh-cn |
| Arabic     | ar    |
| Turkish    | tr    |
| Uzbek      | uz    |
| Kazakh     | kk    |

---

## 🌐 STEP 5 — Host 24/7 (FREE Options)

### Option A: Railway.app (Easiest — Free)
1. Go to https://railway.app → sign up with GitHub
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Upload your bot files to a GitHub repo first:
   ```bash
   git init
   git add .
   git commit -m "init"
   git remote add origin https://github.com/YOUR_USERNAME/translate-bot.git
   git push -u origin main
   ```
4. In Railway, select your repo
5. Add environment variable: `TOKEN` = your bot token
6. In `bot.py`, change the last line to:
   ```python
   TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN_HERE")
   ```
7. Railway auto-detects Python and runs the bot 24/7 ✅

---

### Option B: Render.com (Free)
1. Go to https://render.com → sign up
2. New → **Background Worker**
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `python bot.py`
6. Add env variable: `TOKEN` = your bot token
7. Deploy ✅

---

### Option C: VPS / Your Own PC (Advanced)
Use **PM2** or **screen** to keep it running:
```bash
# With screen:
screen -S translatebot
python bot.py
# Press Ctrl+A then D to detach
```

---

## ⚠️ Important Notes

- The bot uses **Google Translate (free)** — no API key needed
- It **auto-detects** the language of each message
- You can add **multiple pairs** to one channel (e.g. ru→en AND en→ru AND de→en)
- Only users with **Manage Channels** permission can configure it
- Translations appear as an **embed** below each message, similar to Discord's built-in translator
