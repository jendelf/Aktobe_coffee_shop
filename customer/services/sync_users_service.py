import asyncio
import json
import re
from customer.repositories.customer_repository import UserRepository
from database import async_session_maker
from customer.services.crm_service import CRMService
from core.paths import CONFIG, JSON_FILES

TELEGRAM_USERS_FILE = JSON_FILES["telegram_users"]

# Загружаем конфиг
with open(CONFIG, "r", encoding="utf-8") as f:
    config_data = json.load(f)

def extract_contact_from_comment(comment: str) -> str | None:
    """Парсим Telegram из комментария"""
    if not comment:
        return None
    match_tg = re.search(r"(?:@|t\.me/|https://t\.me/)([A-Za-z0-9_]{5,})", comment)
    return match_tg.group(1) if match_tg else None

async def sync_users():
    crm = CRMService(
        layer_name=config_data["LAYER_NAME"],
        username=config_data["USERNAME"],
        password=config_data["PASSWORD"]
    )

    async with async_session_maker() as session:
        repo = UserRepository(session)
        crm_users = crm.get_customers()
        
        print(f"CRM вернул: {len(crm_users)} пользователей")
        for c in crm_users:
            # Берем первый телефон из contactMethods
            contact_methods = c.get("contactMethods", [])
            phone = contact_methods[0]["value"] if contact_methods else None

            data = {
                "crm_id": c.get("id"),
                "name": c.get("firstName"),
                "phone": phone,
                "tg_name": extract_contact_from_comment(c.get("comment")),
                "chat_id": None  # пока пусто
            }

            if not data["crm_id"]:
                print(f"Пропускаем пользователя с пустым crm_id: {data}")
                continue

            print(f"Добавляем/проверяем: {data}")
            await repo.add_if_not_exists(data)

    # Обновляем telegram_users.json
    telegram_users = {}
    for c in crm_users:
        tg_name = extract_contact_from_comment(c.get("comment"))
        if tg_name:
            telegram_users[c.get("id")] = {"tg_name": tg_name, "chat_id": None}

    with open(TELEGRAM_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(telegram_users, f, ensure_ascii=False, indent=2)

    print(f"Маппинг crm_id → tg_name сохранен: {len(telegram_users)} записей")
