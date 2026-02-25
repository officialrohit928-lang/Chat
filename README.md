# 🤖 Sonali AI Chat Bot

A Powerful Telegram AI Chat Bot powered by Groq AI.

This bot replies like a real human using LLaMA3 model via Groq API.

---

## ✨ Features

- 💬 Human-like AI Replies
- ⚡ Fast Response (Groq Powered)
- 🔐 Secure API Key via Environment Variables
- ☁️ One Click Heroku Deploy
- 🧠 Custom Personality Support

---

## 🚀 Deploy to Heroku

Click the button below to deploy your own bot instantly:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/officialrohit928-lang/Chat)

---

## ⚙️ Required Config Vars

Add these in Heroku → Settings → Reveal Config Vars

| Variable Name     | Description          |
|------------------|----------------------|
| GROQ_API_KEY     | Your Groq API Key    |
| API_ID           | Telegram API ID      |
| API_HASH         | Telegram API Hash    |
| BOT_TOKEN        | BotFather Token      |

---

## 🔑 Get Groq API Key

1. Go to https://console.groq.com/
2. Create API Key
3. Add it in Heroku Config Vars

---

## 🛠️ Local Setup

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
cd YOUR_REPO_NAME
pip install -r requirements.txt
python main.py
