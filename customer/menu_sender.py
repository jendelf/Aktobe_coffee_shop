import json
import aiohttp
import asyncio
import aiofiles
from pathlib import Path
from core.paths import JSON_FILES, CONFIG, MENU_FILE_PATH

TELEGRAM_USERS = JSON_FILES["telegram_users.json"]

with CONFIG.open("r", encoding="utf-8") as f:
    config = json.load(f)

with TELEGRAM_USERS.open("r", encoding="utf-8") as f:
    tg_users = json.load(f)
    

TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
MENU_MESSAGE = config.get("MENU_MESSAGE", "Новое меню доступно!")

# Формируем словарь username -> chat_id
username_to_chatid = {
    u["username"].lstrip("@").lower(): u["chat_id"]
    for u in tg_users
    if "username" in u and "chat_id" in u
}
async def send_telegram_message(session, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        async with session.post(url, json=payload) as r:
            if r.status == 200:
                print(f"Сообщение отправлено {chat_id}")
            else:
                text = await r.text()
                print(f"Ошибка {r.status}: {text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения {chat_id}: {e}")

async def send_telegram_file(session, chat_id, file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    data = aiohttp.FormData()
    data.add_field("chat_id", str(chat_id))
    with open(file_path, "rb") as f:  # синхронное открытие файла
        data.add_field("document", f, filename=Path(file_path).name)
    async with session.post(url, data=data) as r:
        if r.status == 200:
            print(f"📎 Файл отправлен {chat_id}")
        else:
            text = await r.text()
            print(f"Ошибка {r.status}: {text}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for u in tg_users:
            chat_id = u["chat_id"]
            tasks.append(send_telegram_message(session, chat_id, MENU_MESSAGE))
            if MENU_FILE_PATH.exists():
                tasks.append(send_telegram_file(session, chat_id, MENU_FILE_PATH))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
