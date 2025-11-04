import json
from customer.services.crm_service import CRMService
from core.paths import JSON_FILES, CONFIG 

CHECKS_FILE = JSON_FILES["receipts"] 

# Загружаем конфиг
with open(CONFIG, "r", encoding="utf-8") as f:
    config_data = json.load(f)

async def sync_checks():
    crm = CRMService(
        layer_name=config_data["LAYER_NAME"],
        username=config_data["USERNAME"],
        password=config_data["PASSWORD"]
    )

    try:
        checks = crm.get_checks()
    except Exception as e:
        print(f"Ошибка при получении чеков из CRM: {e}")
        return

    # Загружаем существующие чеки
    try:
        with open(CHECKS_FILE, "r", encoding="utf-8") as f:
            existing_checks = json.load(f)
    except FileNotFoundError:
        existing_checks = []

    # Добавляем новые чеки без дубликатов
    existing_ids = {c.get("id") for c in existing_checks if c.get("id") is not None}
    new_checks = [c for c in checks if c.get("id") not in existing_ids]
    existing_checks.extend(new_checks)

    with open(CHECKS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_checks, f, ensure_ascii=False, indent=4)

    print(f"Синхронизация чеков завершена: добавлено {len(new_checks)} новых чеков")


async def clear_checks_file():
    with open(CHECKS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    print("Файл с чеками очищен")
