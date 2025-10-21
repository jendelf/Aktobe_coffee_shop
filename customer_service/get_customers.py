import requests
import json
import re
from requests.auth import HTTPBasicAuth
from pathlib import Path

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

LAYER_NAME = CONFIG["LAYER_NAME"]
USERNAME = CONFIG["USERNAME"]
PASSWORD = CONFIG["PASSWORD"]
TELEGRAM_BOT_TOKEN = CONFIG.get("TELEGRAM_BOT_TOKEN")
LIMIT = CONFIG.get("LIMIT", 100)
OFFSET = CONFIG.get("OFFSET", 0)
MENU_MESSAGE = CONFIG.get("MENU_MESSAGE")

URL = f"https://{LAYER_NAME}.quickresto.ru/platform/online/api/list?moduleName=crm.customer&className=ru.edgex.quickresto.modules.crm.customer.CrmCustomer"

headers = {
    "Content-Type": "application/json",
    "Connection": "keep-alive"
}

payload = {"limit": LIMIT, "offset": OFFSET, "filters": []}
params = {"sortFields": ["name"], "sortOrders": ["asc"]}

CUSTOMERS_FILE = Path("customers.json")
CONTACTS_FILE = Path("contacts.json")

# Получаем клиентов из CRM
response = requests.get(
    URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers=headers,
    params=params,
    json=payload
)

if response.status_code != 200:
    print(f"Ошибка {response.status_code}: {response.text}")
    exit()

customers = response.json()
print(f"Получено клиентов: {len(customers)}")

# Сохраняем алиентов
with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
    json.dump(customers, f, ensure_ascii=False, indent=2)


# парсим контакты из комента
def extract_contact_from_comment(comment: str):
    if not comment:
        return None, None

    telegram = None

    match_tg = re.search(r"(?:@|t\.me/|https://t\.me/)([A-Za-z0-9_]{5,})", comment)
    if match_tg:
        telegram = match_tg.group(1)

    return telegram

contacts = []
crm_to_tg = {}  # словарь для маппинга айди из CRM и айди чата

for customer in customers:
    crm_id = customer.get("id")
    name = customer.get("firstName")
    comment = customer.get("comment")

    telegram = extract_contact_from_comment(comment)

    contacts.append({
        "crm_id": crm_id,
        "name": name,
        "phone": customer.get("contactMethods"),
        "telegram": telegram
    })

    if telegram:
        crm_to_tg[crm_id] = telegram  # Мапим айди из CRM и айди чата

with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=2)

with open("crm_to_telegram.json", "w", encoding="utf-8") as f:
    json.dump(crm_to_tg, f, ensure_ascii=False, indent=2)
