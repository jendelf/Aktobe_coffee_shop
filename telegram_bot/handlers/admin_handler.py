from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from telegram_bot.handlers.send_menu_handler import send_menu, send_telegram_message
from core.paths import JSON_FILES, MENU_FILE_PATH
from telegram_bot.bot_config import users
import json
import aiohttp
import asyncio
import os

router = Router()

ADMINS_FILE = JSON_FILES["admins"]

class AdminStates(StatesGroup):
    waiting_for_menu_file = State()
    waiting_for_promo = State()

os.makedirs(MENU_FILE_PATH, exist_ok=True)  # создаём папку menus, если нет

# ------------------- Вспомогательные функции -------------------

def get_admins() -> list[int]:
    if not ADMINS_FILE.exists():
        return []
    with open(ADMINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_latest_menu_file():
    """Возвращает последний загруженный файл меню или None"""
    files = list(MENU_FILE_PATH.glob("*.*"))
    if not files:
        return None
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0]

# ------------------- Панель администратора -------------------

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in get_admins():
        return await message.answer("⛔ У вас нет доступа к панели администратора.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👀 Посмотреть меню", callback_data="view_menu")],
        [InlineKeyboardButton(text="📎 Загрузить меню", callback_data="upload_menu")],
        [InlineKeyboardButton(text="☕ Отправить меню", callback_data="send_menu")],
        [InlineKeyboardButton(text="📢 Разослать акцию", callback_data="send_promo")]
    ])
    await message.answer("📋 Панель администратора", reply_markup=keyboard)

# ------------------- Загрузка меню -------------------

@router.callback_query(F.data == "upload_menu")
async def ask_for_menu_file(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.from_user.id not in get_admins():
        return await callback.answer("⛔ Нет доступа.", show_alert=True)

    await callback.message.answer("📎 Отправь новый файл меню (PDF/JPG/PNG).")
    await state.set_state(AdminStates.waiting_for_menu_file)
    await callback.answer()

@router.message(F.document, StateFilter(AdminStates.waiting_for_menu_file))
async def handle_new_menu_file(message: Message, state: FSMContext):
    if message.from_user.id not in get_admins():
        return

    file = message.document
    file_path = MENU_FILE_PATH / file.file_name

    try:
        await message.bot.download(file, destination=file_path)
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке файла: {e}")
        await state.clear()
        return

    await message.answer(f"✅ Меню успешно загружено!\nФайл сохранён как: `{file.file_name}`")
    await state.clear()

# ------------------- Просмотр текущего меню -------------------

@router.callback_query(F.data == "view_menu")
async def view_current_menu(callback: CallbackQuery):
    if callback.from_user.id not in get_admins():
        return await callback.answer("⛔ Нет доступа.", show_alert=True)

    latest_file = get_latest_menu_file()
    if not latest_file:
        return await callback.message.answer("⚠️ Меню ещё не загружено.")

    # Исправлено здесь
    await callback.message.answer_document(document=FSInputFile(latest_file), caption=f"📄 Текущее меню: {latest_file.name}")
    await callback.answer()

# ------------------- Отправка меню -------------------

@router.callback_query(F.data == "send_menu")
async def send_menu_callback(callback: CallbackQuery):
    if callback.from_user.id not in get_admins():
        return await callback.answer("⛔ Нет доступа.", show_alert=True)

    latest_file = get_latest_menu_file()
    if not latest_file:
        return await callback.message.answer("⚠️ Меню ещё не загружено.")

    await send_menu(callback.message, callback.bot)
    await callback.answer()

# ------------------- Рассылка акции -------------------

@router.callback_query(lambda c: c.data == "send_promo")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📢 Введи текст акции:")
    await state.set_state(AdminStates.waiting_for_promo)
    await callback.answer()

@router.message(F.text, StateFilter(AdminStates.waiting_for_promo))
async def broadcast_message(message: Message, state: FSMContext):
    await state.clear()

    # Читаем пользователей из файла
    try:
        with open(JSON_FILES["telegram_users"], "r", encoding="utf-8") as f:
            telegram_users = json.load(f)  # ожидаем список словарей
    except FileNotFoundError:
        telegram_users = []

    if not telegram_users:
        return await message.answer("Нет зарегистрированных пользователей для рассылки.")

    bot = message.bot
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in telegram_users:
            chat_id = user.get("chat_id")
            if chat_id:  # отправляем только тем, у кого есть chat_id
                tasks.append(send_telegram_message(session, chat_id, message.text, bot.token))

        if tasks:
            await asyncio.gather(*tasks)

    await message.answer("✅ Акция отправлена всем пользователям.")

