import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from deep_translator import GoogleTranslator

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
TOKEN = os.environ.get("TOKEN", "")
CONFIG_FILE = "channel_config.json"

LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "zh-CN": "Chinese Simplified",
    "zh-TW": "Chinese Traditional", "hr": "Croatian", "cs": "Czech",
    "da": "Danish", "nl": "Dutch", "en": "English", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "he": "Hebrew",
    "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic", "id": "Indonesian",
    "ga": "Irish", "it": "Italian", "ja": "Japanese", "kn": "Kannada",
    "kk": "Kazakh", "ko": "Korean", "ky": "Kyrgyz", "lv": "Latvian",
    "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay", "ml": "Malayalam",
    "mt": "Maltese", "mr": "Marathi", "mn": "Mongolian", "ne": "Nepali",
    "no": "Norwegian", "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian", "sr": "Serbian",
    "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "sw": "Swahili", "sv": "Swedish", "tl": "Filipino", "tg": "Tajik",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek",
    "vi": "Vietnamese", "cy": "Welsh", "yi": "Yiddish", "zu": "Zulu"
}

# ─────────────────────────────────────────
#  LOAD / SAVE CONFIG
# ─────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

channel_config = load_config()

# ─────────────────────────────────────────
#  BOT SETUP
# ─────────────────────────────────────────
intents = discord.Intents.all()   # ← enable ALL intents
bot = commands.Bot(command_prefix="!", intents=intents)

def try_translate(text, src, dest):
    try:
        result = GoogleTranslator(source=src, target=dest).translate(text)
        if result and result.strip().lower() != text.strip().lower():
            return result.strip()
    except Exception as e:
        print(f"  translate error {src}→{dest}: {e}")
    return None

# ─────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"📋 Loaded config: {channel_config}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")


@bot.event
async def on_message(message):
    # Print EVERY message including bots so we know it's firing
    print(f"📨 Message from {message.author} in #{message.channel.name} (ID:{message.channel.id}): {message.content[:50]}")

    if message.author.bot:
        await bot.process_commands(message)
        return

    channel_id = str(message.channel.id)
    cfg = channel_config.get(channel_id)

    print(f"   Config for this channel: {cfg}")

    if cfg and cfg.get("enabled") and cfg.get("pairs"):
        text = message.content.strip()

        if not text or text.startswith("!") or text.startswith("/"):
            await bot.process_commands(message)
            return

        translations_done = []
        seen_results = set()

        for src, dest in cfg["pairs"]:
            translated = try_translate(text, src, dest)
            print(f"  Trying {src}→{dest}: {translated}")
            if translated and translated not in seen_results:
                translations_done.append((src, dest, translated))
                seen_results.add(translated)

        if translations_done:
            embed = discord.Embed(color=0x5865F2)
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )
            embed.add_field(name="🌐 Original", value=text[:1024], inline=False)
            for src, dest, translated in translations_done:
                src_name  = LANGUAGES.get(src, src).title()
                dest_name = LANGUAGES.get(dest, dest).title()
                embed.add_field(
                    name=f"🔁 {src_name} → {dest_name}",
                    value=translated[:1024],
                    inline=False
                )
            embed.set_footer(text="Auto Translate Bot • Google Translate")
            await message.channel.send(embed=embed)
        else:
            print("  ⚠️ No translation produced")
    else:
        print(f"   ⚠️ Channel not configured or disabled. Configured channels: {list(channel_config.keys())}")

    await bot.process_commands(message)


# ─────────────────────────────────────────
#  PREFIX COMMAND — type !ping in Discord to test
# ─────────────────────────────────────────
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Bot is working and reading messages!")


# ─────────────────────────────────────────
#  SLASH COMMANDS
# ─────────────────────────────────────────

@bot.tree.command(name="translate_setup", description="Add a language pair for auto-translation in this channel")
@app_commands.describe(from_lang="Source language code (e.g. ru, en, de)", to_lang="Target language code (e.g. en, ru)")
@app_commands.checks.has_permissions(manage_channels=True)
async def translate_setup(interaction: discord.Interaction, from_lang: str, to_lang: str):
    from_lang, to_lang = from_lang.strip().lower(), to_lang.strip().lower()
    channel_id = str(interaction.channel_id)

    if channel_id not in channel_config:
        channel_config[channel_id] = {"pairs": [], "enabled": True}

    pair = [from_lang, to_lang]
    if pair not in channel_config[channel_id]["pairs"]:
        channel_config[channel_id]["pairs"].append(pair)
        channel_config[channel_id]["enabled"] = True
        save_config(channel_config)
        src_name  = LANGUAGES.get(from_lang, from_lang).title()
        dest_name = LANGUAGES.get(to_lang, to_lang).title()
        await interaction.response.send_message(f"✅ Added: **{src_name}** → **{dest_name}**")
    else:
        await interaction.response.send_message("ℹ️ That pair already exists.", ephemeral=True)


@bot.tree.command(name="translate_remove", description="Remove a language pair from this channel")
@app_commands.describe(from_lang="Source language code", to_lang="Target language code")
@app_commands.checks.has_permissions(manage_channels=True)
async def translate_remove(interaction: discord.Interaction, from_lang: str, to_lang: str):
    channel_id = str(interaction.channel_id)
    pair = [from_lang.lower(), to_lang.lower()]
    if channel_id in channel_config and pair in channel_config[channel_id]["pairs"]:
        channel_config[channel_id]["pairs"].remove(pair)
        save_config(channel_config)
        await interaction.response.send_message(f"✅ Removed `{from_lang}` → `{to_lang}`.")
    else:
        await interaction.response.send_message("❌ That pair wasn't found.", ephemeral=True)


@bot.tree.command(name="translate_on", description="Enable auto-translation in this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def translate_on(interaction: discord.Interaction):
    channel_id = str(interaction.channel_id)
    if channel_id not in channel_config or not channel_config[channel_id].get("pairs"):
        await interaction.response.send_message("❌ No pairs set. Use `/translate_setup` first.", ephemeral=True)
        return
    channel_config[channel_id]["enabled"] = True
    save_config(channel_config)
    await interaction.response.send_message("✅ Auto-translation **enabled**.")


@bot.tree.command(name="translate_off", description="Disable auto-translation in this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def translate_off(interaction: discord.Interaction):
    channel_id = str(interaction.channel_id)
    if channel_id in channel_config:
        channel_config[channel_id]["enabled"] = False
        save_config(channel_config)
    await interaction.response.send_message("🔇 Auto-translation **disabled**.")


@bot.tree.command(name="translate_status", description="Show translation settings for this channel")
async def translate_status(interaction: discord.Interaction):
    channel_id = str(interaction.channel_id)
    cfg = channel_config.get(channel_id)
    if not cfg or not cfg.get("pairs"):
        await interaction.response.send_message("ℹ️ No pairs configured for this channel.", ephemeral=True)
        return
    status = "✅ Enabled" if cfg.get("enabled") else "🔇 Disabled"
    pairs_text = "\n".join(
        f"• `{s}` ({LANGUAGES.get(s, s)}) → `{d}` ({LANGUAGES.get(d, d)})"
        for s, d in cfg["pairs"]
    )
    embed = discord.Embed(title="🌐 Translation Settings", color=0x5865F2)
    embed.add_field(name="Status", value=status, inline=False)
    embed.add_field(name="Language Pairs", value=pairs_text, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="translate_once", description="Translate a specific text once")
@app_commands.describe(text="Text to translate", to_lang="Target language code (e.g. en, ru)")
async def translate_once(interaction: discord.Interaction, text: str, to_lang: str):
    await interaction.response.defer()
    try:
        result = GoogleTranslator(source='auto', target=to_lang.lower()).translate(text)
        dest_name = LANGUAGES.get(to_lang.lower(), to_lang).title()
        embed = discord.Embed(title="🔁 Translation", color=0x57F287)
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name=f"Translated ({dest_name})", value=result[:1024], inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
bot.run(TOKEN)
