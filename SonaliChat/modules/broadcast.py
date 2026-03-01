import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from SonaliChat import app
from SonaliChat.database import get_chats
from config import OWNER_ID

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_(_, message: Message):

    reply = message.reply_to_message
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None

    if not reply and not text:
        return await message.reply_text("Reply karo ya text do.")

    progress_msg = await message.reply_text("Broadcasting...")

    sent_groups = sent_users = failed = pinned = 0
    data = await get_chats()

    recipients = data.get("chats", []) + data.get("users", [])

    for chat_id in recipients:
        try:
            if reply:
                msg = await reply.copy(chat_id)
            else:
                msg = await app.send_message(chat_id, text=text)

            if chat_id < 0:
                sent_groups += 1
                try:
                    await msg.pin(disable_notification=True)
                    pinned += 1
                except:
                    pass
            else:
                sent_users += 1

            await asyncio.sleep(0.3)

        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception as e:
            print(f"Failed {chat_id}: {e}")
            failed += 1

    await progress_msg.edit_text(
        f"Broadcast Complete\n\n"
        f"Groups: {sent_groups}\n"
        f"Users: {sent_users}\n"
        f"Pinned: {pinned}\n"
        f"Failed: {failed}"
    )
