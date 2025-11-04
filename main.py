import asyncio
from aiogram import Bot, Dispatcher
from telegram_bot.handlers import admin_handler, send_menu_handler, today_stat_handler, start_handler
from telegram_bot.bot_config import TELEGRAM_BOT_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from customer.services.sync_users_service import sync_users
from customer.services.sync_checks_service import sync_checks, clear_checks_file

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(start_handler.router)
dp.include_router(send_menu_handler.router)
dp.include_router(today_stat_handler.router)
dp.include_router(admin_handler.router)

# Scheduler
scheduler = AsyncIOScheduler()

# Настраиваем задачи
scheduler.add_job(sync_users, "cron", hour=2, minute=0)      # Пользователи каждый день в 02:00
scheduler.add_job(sync_checks, "interval", minutes=10)       # Чеки каждые 10 минут
scheduler.add_job(clear_checks_file, "cron", hour=23, minute=59)  # Очистка чеков в 23:59

async def main():
    print("Начинаем синхронизацию пользователей и чеков перед стартом бота...")

    # Синхронизируем пользователей и чеки **перед запуском polling**
    await sync_users()   # теперь insert в базу происходит только после получения данных из CRM
    await sync_checks()  # синхронизация чеков

    print("Синхронизация завершена ✅")

    # Запускаем scheduler внутри event loop
    scheduler.start()

    print("Бот запущен 🚀")
    # Запускаем polling бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
