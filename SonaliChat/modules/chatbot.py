from pyrogram import Client, filters
from pyrogram.types import Message
from openai import OpenAI
from config import GROQ_API_KEY

# Groq Client Setup
ai_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# AI Response Function
async def get_ai_response(user_text: str):
    try:
        completion = ai_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly Telegram user. "
                               "Reply naturally, short and casual. "
                               "Don't sound like AI."
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.8,
            max_tokens=500,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return "⚠️ AI Error: Try again later."


# Private Chat Handler
@Client.on_message(filters.private & filters.text)
async def chatbot_handler(client: Client, message: Message):

    user_text = message.text

    # typing effect
    await client.send_chat_action(message.chat.id, "typing")

    reply = await get_ai_response(user_text)

    await message.reply_text(reply)
