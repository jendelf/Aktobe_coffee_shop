import asyncio
import aiohttp
from pathlib import Path
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from core.paths import MENU_FILE_PATH
from telegram_bot.bot_config import users

router = Router()

async def send_telegram_message(session, chat_id, message, bot_token):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        async with session.post(url, json=payload) as r:
            if r.status == 200:
                print(f"Сообщение отправлено {chat_id}")
            else:
                text = await r.text()
                print(f"Ошибка {r.status}: {text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения {chat_id}: {e}")

async def send_telegram_file(session, chat_id, file_path, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    data = aiohttp.FormData()
    data.add_field("chat_id", str(chat_id))
    with open(file_path, "rb") as f:
        data.add_field("document", f, filename=Path(file_path).name)
    async with session.post(url, data=data) as r:
        if r.status == 200:
            print(f"📎 Файл отправлен {chat_id}")
        else:
            text = await r.text()
            print(f"Ошибка {r.status}: {text}")

@router.message(Command("send_menu"))
async def send_menu_handler(message: Message, bot: Bot):
    if not users:
        await message.reply("Нет зарегистрированных пользователей для рассылки.")
        return

    async with aiohttp.ClientSession() as session:
        tasks = []
        for u in users:
            chat_id = u["chat_id"]
            tasks.append(send_telegram_message(session, chat_id, "📋 Новое меню доступно!", bot.token))
            if MENU_FILE_PATH.exists():
                tasks.append(send_telegram_file(session, chat_id, MENU_FILE_PATH, bot.token))
        await asyncio.gather(*tasks)

    await message.reply("Меню отправлено всем пользователям.")
