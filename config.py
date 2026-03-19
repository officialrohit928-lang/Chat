import asyncio
import random
import os
import aiohttp
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatType
from dotenv import load_dotenv

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
USER_SESSION = os.getenv("USER_SESSION")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LOGGER_GROUP_ID = int(os.getenv("LOGGER_GROUP_ID", 0))
BOT_USERNAME = os.getenv("BOT_USERNAME", "Sonalichatbot")

STICKER = [
    "CAACAgUAAxkBAAKV2Ge_HEejUGb8foZZ9eunAivt46rNAAL9EQAC-EXwV3yNmpSjijuwHgQ",
    "CAACAgUAAxkBAAKV12e_HEUWk7Dr9lPFRy0YJ2W_aZQnAAIgEgACRnzxV6MUtKkl8-lcHgQ",
]

IMG = [
    "https://graph.org/file/eaa3a2602e43844a488a5.jpg",
    "https://graph.org/file/b129e98b6e5c4db81c15f.jpg",
]

START = "👋 Hello! I am Sonali, your AI assistant 😎"
HELP_READ = "📖 This is the help section"
HELP_ABOUT = "ℹ️ About Sonali AI"
STBUTTON = [[InlineKeyboardButton("ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="back")]]

# -------------------------
# BOT CLIENT
# -------------------------
app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -------------------------
# USERBOT CLIENT
# -------------------------
userbot = Client(
    "userbot",
    session_string=USER_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

# -------------------------
# GROQ API FUNCTION
# -------------------------
async def groq_ask(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "Groq API key missing 😅"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are Sonali, friendly Indian girl. Reply in short Hinglish."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.9
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_text = await resp.text()
                print("Groq Error:", error_text)
                return "Server busy 😅 try again later"

# -------------------------
# BOT HANDLERS
# -------------------------
@app.on_message(filters.text & ~filters.command(["start", "aistart", "help"]))
async def chat_reply(client, message: Message):
    if message.from_user.is_bot:
        return

    bot = await client.get_me()
    bot_username = bot.username.lower()
    text = message.text.lower()
    trigger = False

    if not message.reply_to_message:
        trigger = True
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        trigger = True
    if f"@{bot_username}" in text or "sonali" in text:
        trigger = True
    if not trigger:
        return

    response = await groq_ask(message.text)
    await message.reply_text(response)

# Start / aistart command
@app.on_message(filters.command(["start", "aistart"]) & ~filters.bot)
async def start(client, m: Message):
    bot = await client.get_me()
    if STICKER:
        await m.reply_sticker(random.choice(STICKER))
    await m.reply_photo(
        photo=random.choice(IMG),
        caption=START,
        reply_markup=InlineKeyboardMarkup(STBUTTON)
    )

# Callback query handlers
@app.on_callback_query(filters.regex("back"))
async def back_menu(client, cq):
    await cq.message.edit_text(text=START, reply_markup=InlineKeyboardMarkup(STBUTTON))

# -------------------------
# USERBOT HANDLERS
# -------------------------
@userbot.on_message(filters.text & ~filters.me)
async def userbot_chat(client, message: Message):
    text = message.text.lower()
    trigger = False

    if not message.reply_to_message:
        trigger = True
    if message.reply_to_message and message.reply_to_message.from_user.is_self:
        trigger = True
    if "sonali" in text:
        trigger = True
    if not trigger:
        return

    response = await groq_ask(message.text)
    await message.reply_text(response)

# -------------------------
# RUN BOT + USERBOT
# -------------------------
async def main():
    await asyncio.gather(
        app.start(),
        userbot.start()
    )
    print("✅ Bot + Userbot dono chal rahe hain 😎")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
