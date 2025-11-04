import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.paths import JSON_FILES

router = Router()

ADMINS_FILE = JSON_FILES["admins"]
TELEGRAM_USERS_FILE = JSON_FILES["telegram_users"]
EXPECTED_TOKEN = "mvp-test-token"


def get_admins() -> list[int]:
    """Загрузка списка админов"""
    try:
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []


def save_admins(admins: list[int]):
    """Сохранение списка админов"""
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(admins, f, ensure_ascii=False, indent=2)


def get_telegram_users() -> list[dict]:
    """Загрузка пользователей Telegram"""
    try:
        with open(TELEGRAM_USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [u for u in data if isinstance(u, dict) and "chat_id" in u]
            return []
    except FileNotFoundError:
        return []


def save_telegram_users(users: list[dict]):
    """Сохранение пользователей Telegram"""
    with open(TELEGRAM_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    text_arg = message.text.split(maxsplit=1)
    token_arg = text_arg[1].strip() if len(text_arg) > 1 else None

    # Приветственное сообщение
    welcome_msg = f"Привет, {username or 'пользователь'}! Добро пожаловать в бота."

    await message.reply(welcome_msg)

    # Регистрация админа по токену
    if token_arg == EXPECTED_TOKEN:
        admins = get_admins()
        if user_id not in admins:
            admins.append(user_id)
            save_admins(admins)
            await message.reply("✅ Вы зарегистрированы как администратор и можете использовать /today.")
        else:
            await message.reply("Вы уже зарегистрированы как администратор.")
        return

    # Добавление пользователя в telegram_users.json
    users = get_telegram_users()
    if not any(u["chat_id"] == user_id for u in users):
        users.append({"chat_id": user_id, "username": username})
        save_telegram_users(users)
        await message.reply("✅ Вы добавлены в список пользователей для рассылки.")
    else:
        await message.reply("Вы уже в списке пользователей для рассылки.")
