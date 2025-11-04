import asyncio
import aiohttp
from pathlib import Path
from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile
from core.paths import MENU_FILE_PATH, JSON_FILES
import json

router = Router()

def get_latest_menu_file() -> Path | None:
    """Возвращает последний загруженный файл меню или None"""
    if not MENU_FILE_PATH.exists() or not any(MENU_FILE_PATH.iterdir()):
        return None
    files = list(MENU_FILE_PATH.glob("*.*"))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0]

async def send_telegram_message(session, chat_id, message, bot_token):
    """Отправка обычного текста через aiohttp"""
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

async def send_menu(message: Message, bot: Bot):
    """Рассылка меню всем пользователям"""
    latest_file = get_latest_menu_file()
    if not latest_file:
        return await message.reply("⚠️ Меню ещё не загружено.")

    # Загружаем пользователей из telegram_users.json
    try:
        with open(JSON_FILES["telegram_users"], "r", encoding="utf-8") as f:
            telegram_users = json.load(f)
    except FileNotFoundError:
        return await message.reply("Нет зарегистрированных пользователей для рассылки.")
    except json.JSONDecodeError:
        return await message.reply("Ошибка при чтении файла с пользователями.")

    if not telegram_users:
        return await message.reply("Нет зарегистрированных пользователей для рассылки.")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in telegram_users:
            chat_id = user.get("chat_id")
            if not chat_id:
                continue
            # Отправляем текстовое уведомление
            tasks.append(send_telegram_message(session, chat_id, "📋 Новое меню доступно!", bot.token))
            # Отправляем файл через Aiogram
            tasks.append(bot.send_document(chat_id, FSInputFile(latest_file)))

        if tasks:
            await asyncio.gather(*tasks)

    await message.reply(f"✅ Меню {latest_file.name} отправлено всем пользователям.")
