import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from core.paths import JSON_FILES

router = Router()

ADMINS_FILE = JSON_FILES["admins"]
EXPECTED_TOKEN = "mvp-test-token"

def get_admins():
    try:
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@router.message(Command("start"))
async def start_handler(message: Message):
    arg = message.get_args().strip()

    if arg != EXPECTED_TOKEN:
        await message.reply("Привет! Но вы не зарегистрированы как админ.")
        return

    admins = get_admins()
    user_id = message.from_user.id

    if user_id not in admins:
        admins.append(user_id)
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(admins, f, ensure_ascii=False, indent=2)
        await message.reply("✅ Вы зарегистрированы как администратор и можете использовать /today.")
    else:
        await message.reply("Вы уже зарегистрированы как администратор.")

