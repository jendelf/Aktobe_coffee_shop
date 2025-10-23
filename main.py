import asyncio
from telegram_bot.bot_config import bot, dp

from telegram_bot.handlers import start_handler
from telegram_bot.handlers import send_menu_handler
from telegram_bot.handlers import today_stat_handler

# Регистрируем все роутеры
dp.include_router(start_handler.router)
dp.include_router(send_menu_handler.router)
dp.include_router(today_stat_handler.router)

if __name__ == "__main__":
    print("Бот запущен 🚀")
    asyncio.run(dp.start_polling(bot))
