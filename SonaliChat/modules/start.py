import asyncio
import random
import os
import aiohttp

from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatType

# -------------------------
# CONFIG (Heroku config vars)
# -------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
USER_SESSION = os.environ.get("USER_SESSION")        # String session for userbot
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LOGGER_GROUP_ID = int(os.environ.get("LOGGER_GROUP_ID", 0))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "SonaliChatBot")

# Optional assets
STICKER = []      # list of sticker file_ids
IMG = []          # list of photo URLs
FSUB = False      # force subscribe
START = "👋 Hello! I am Sonali, your AI assistant 😎"
HELP_READ = "📖 This is the help section"
HELP_ABOUT = "ℹ️ About Sonali AI"
STBUTTON = [[InlineKeyboardButton("ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="back")]]

# -------------------------
# DATABASE MOCK (replace with real)
# -------------------------
chatsdb = {}   # dummy dictionary, replace with MongoDB or SQLite
async def add_user(user_id, username=None):
    chatsdb[user_id] = {"username": username}
async def add_chat(chat_id, chat_title):
    chatsdb[chat_id] = {"title": chat_title}
async def get_fsub(client, m): return True   # placeholder

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
    if FSUB and not await get_fsub(client, m):
        return

    user_id = m.from_user.id
    await add_user(user_id, m.from_user.username or None)

    if STICKER and isinstance(STICKER, list):
        sticker_to_send = random.choice(STICKER)
        umm = await m.reply_sticker(sticker=sticker_to_send)
        await asyncio.sleep(1)
        await umm.delete()

    log_msg = f"**✦ ηєᴡ ᴜsєʀ sᴛᴧʀᴛєᴅ ᴛʜє ʙσᴛ**\n\n**➻ ᴜsєʀ :** [{m.from_user.first_name}](tg://user?id={user_id})\n**➻ ɪᴅ :** `{user_id}`"
    if LOGGER_GROUP_ID:
        await client.send_message(LOGGER_GROUP_ID, log_msg)

    accha = await m.reply_text(text="**ꜱᴛᴧʀᴛɪηɢ....🥀**")
    await asyncio.sleep(1)
    await accha.edit("**ᴘɪηɢ ᴘσηɢ...🍫**")
    await asyncio.sleep(0.5)
    await accha.edit("**ꜱᴛᴧʀᴛєᴅ.....😱**")
    await asyncio.sleep(0.5)
    await accha.delete()

    await m.reply_photo(
        photo=random.choice(IMG) if IMG else None,
        caption=START,
        reply_markup=InlineKeyboardMarkup(STBUTTON)
    )

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
# CALLBACK QUERY HANDLERS
# -------------------------
@app.on_callback_query(filters.regex('back'))
async def back_to_menu(client, callback_query):
    await callback_query.message.edit_text(
        text=START,
        reply_markup=InlineKeyboardMarkup(STBUTTON),
    )

@app.on_callback_query(filters.regex('HELP_BACK'))
async def help_back(client, callback_query):
    await callback_query.message.edit_text(
        text=START,
        reply_markup=InlineKeyboardMarkup(STBUTTON)
    )

@app.on_callback_query(filters.regex('ABOUT'))
async def about_section(client, callback_query):
    await callback_query.message.edit_text(
        text=HELP_ABOUT,
        reply_markup=InlineKeyboardMarkup(STBUTTON)
    )

# -------------------------
# GROUP ADD / LEFT HANDLERS
# -------------------------
@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client, message: Message):
    if (await client.get_me()).id in [u.id for u in message.new_chat_members]:
        chat_id = message.chat.id
        chat_title = message.chat.title
        await add_chat(chat_id, chat_title)

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client, message: Message):
    if (await client.get_me()).id == message.left_chat_member.id:
        chat_id = message.chat.id
        chatsdb.pop(chat_id, None)

# -------------------------
# MAIN FUNCTION TO RUN BOTH
# -------------------------
async def main():
    await asyncio.gather(
        app.start(),      # start bot
        userbot.start()   # start userbot
    )
    print("✅ Bot + Userbot dono chal rahe hain 😎")
    await idle()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
