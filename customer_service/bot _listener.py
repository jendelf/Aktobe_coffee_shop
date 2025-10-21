import telebot
import json
from pathlib import Path

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

TELEGRAM_BOT_TOKEN = CONFIG["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
USERS_FILE = Path("telegram_users.json")

if USERS_FILE.exists():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []

@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    chat_id = message.chat.id

    if not any(u["chat_id"] == chat_id for u in users):
        users.append({"chat_id": chat_id, "username": username})
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        bot.reply_to(message, "Привет! Теперь я смогу присылать тебе меню")
    else:
        bot.reply_to(message, "Ты уже зарегистрирован ")

bot.polling(none_stop=True)
