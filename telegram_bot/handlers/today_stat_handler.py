import json
from datetime import datetime
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from core.paths import JSON_FILES

router = Router()

RECEIPTS_FILE = JSON_FILES["receipts"]
ADMINS_FILE = JSON_FILES["admins"]

def get_admins() -> list[int]:
    try:
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def is_admin(user_id: int) -> bool:
    return user_id in get_admins()

async def send_today_receipts(bot: Bot):
    try:
        with open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
            receipts = json.load(f)
    except FileNotFoundError:
        print("❌ receipts.json не найден")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    filtered = [
        r for r in receipts 
        if str(r.get("Закрыт", "")).startswith(today_str)
    ]

    if not filtered:
        print("ℹ️ Нет чеков за сегодня")
        return

    total_sum = 0
    lines = []

    for r in filtered:
        total = r.get("Сумма по чеку, ₸", 0)
        order_id = r.get("Номер чека", "N/A")
        date = r.get("Закрыт", "N/A")

        try:
            total_sum += float(total)
        except (ValueError, TypeError):
            pass

        lines.append(f"📌 Чек {order_id}\n📅 {date}\n💰 Сумма: {total}")

    text = "\n\n".join(lines)
    text += f"\n\n📊 Всего чеков: {len(filtered)}\n💵 Общая сумма: {total_sum}"

    for admin_id in get_admins():
        await bot.send_message(admin_id, text)

@router.message(Command("today"))
async def today_handler(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.reply("⛔ У вас нет прав.")
        return
    await message.reply("📊 Сводка за сегодня:")
    await send_today_receipts(bot)
