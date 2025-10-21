import json
from pathlib import Path
import aiohttp
import asyncio

BASE_DIR = Path(__file__).parent

# Пути к файлам
CONFIG_FILE = Path("config.json")
USERS_FILE = BASE_DIR / "telegram_users.json"

# Загружаем конфиг
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

TELEGRAM_BOT_TOKEN = CONFIG.get("TELEGRAM_BOT_TOKEN")
MENU_MESSAGE = CONFIG.get("MENU_MESSAGE", "Новое меню доступно!")
MENU_FILE_PATH = CONFIG.get("MENU_FILE_PATH")

# Загружаем всех пользователей
with open(USERS_FILE, "r", encoding="utf-8") as f:
    tg_users = json.load(f)

# Формируем словарь username → chat_id
username_to_chatid = {
    u["username"].lstrip("@").lower(): u["chat_id"]
    for u in tg_users
    if "username" in u and "chat_id" in u
}

async def send_telegram_message(session, chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    async with session.post(url, json=payload) as r:
        if r.status == 200:
            print(f"Сообщение отправлено {chat_id}")
        else:
            text = await r.text()
            print(f"Ошибка {r.status}: {text}")

async def send_telegram_file(session, chat_id, file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    data = aiohttp.FormData()
    data.add_field("chat_id", str(chat_id))
    data.add_field("document", open(file_path, "rb"), filename=Path(file_path).name)
    async with session.post(url, data=data) as r:
        if r.status == 200:
            print(f"📎 Файл отправлен {chat_id}")
        else:
            text = await r.text()
            print(f"Ошибка {r.status}: {text}")

async def main():
    async with aiohttp.ClientSession() as session:
        for u in tg_users:
            chat_id = u["chat_id"]
            await send_telegram_message(session, chat_id, MENU_MESSAGE)
            if MENU_FILE_PATH:
                await send_telegram_file(session, chat_id, MENU_FILE_PATH)

if __name__ == "__main__":
    asyncio.run(main())
