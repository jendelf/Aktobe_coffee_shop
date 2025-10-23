import json
from aiogram import Bot, Dispatcher
from core.paths import JSON_FILES, CONFIG

# Загружаем конфиг
with CONFIG.open("r", encoding="utf-8") as f:
    CONFIG = json.load(f)

TG_USERS_FILE = JSON_FILES["telegram_users"]
TELEGRAM_BOT_TOKEN = CONFIG["TELEGRAM_BOT_TOKEN"]

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

if TG_USERS_FILE.exists():
    with open(TG_USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []
