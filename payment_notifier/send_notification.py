import json
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from datetime import datetime

CONFIG_FILE = Path("config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)
TELEGRAM_BOT_TOKEN = CONFIG.get("TELEGRAM_BOT_TOKEN")
RECEIPTS_FILE = Path("receipts.json")
EXPECTED_TOKEN = "mvp-test-token"  
ADMINS_FILE = Path("admins.json")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def get_admins():
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
        print("receipts.json не найден")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    filtered_receipts = []

    for r in receipts:
        closed = r.get("Закрыт", "")
        if closed.startswith(today_str):  # только за сегодня
            filtered_receipts.append(r)

    if not filtered_receipts:
        print("Нет чеков за сегодня")
        return

    lines = []
    total_sum = 0
    total_count = 0

    for r in filtered_receipts:
        order_id = r.get("Номер чека", "N/A")
        total = r.get("Сумма по чеку, ₸", 0)
        date = r.get("Закрыт", "N/A")

        try:
            total_sum += float(total)
        except (ValueError, TypeError):
            pass

        total_count += 1
        lines.append(f"📌 Чек {order_id}\n📅 {date}\n💰 Сумма: {total}")

    summary_text = "\n\n".join(lines)
    summary_text += f"\n\n📊 Всего чеков: {total_count}\n💵 Общая сумма: {total_sum}"

    for admin_id in get_admins():
        await bot.send_message(admin_id, summary_text)

@dp.message(Command("start"))
async def on_start(message: Message):
    arg = message.get_args().strip()
    if arg != EXPECTED_TOKEN:
        await message.reply("Привет! Но вы не зарегистрированы как админ.")
        return

    admins = get_admins()
    if message.from_user.id not in admins:
        admins.append(message.from_user.id)
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(admins, f)
        await message.reply("✅ Вы зарегистрированы как администратор и можете использовать /today.")
    else:
        await message.reply("Вы уже зарегистрированы как администратор.")

@dp.message(Command("today"))
async def today_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("⛔ У вас нет прав.")
        return
    await message.reply("Сводка за сегодня:")
    await send_today_receipts(bot)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))