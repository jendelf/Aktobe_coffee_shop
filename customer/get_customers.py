import requests
import json
import re
from requests.auth import HTTPBasicAuth
from core.paths import CONFIG, JSON_FILES

with CONFIG.open("r", encoding= "utf-8") as f:
    config = json.load(f)

CRM_TO_TG_FILE = JSON_FILES["crm_to_telegram"]
CUSTOMERS_FILE = JSON_FILES["customers"]
CONTACTS_FILE = JSON_FILES["contacts"]

LAYER_NAME = config["LAYER_NAME"]
USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]
LIMIT = config.get("LIMIT", 100)
OFFSET = config.get("OFFSET", 0)

URL = f"https://{LAYER_NAME}.quickresto.ru/platform/online/api/list?moduleName=crm.accounting.account.type&className=ru.edgex.quickresto.modules.crm.accounting.account.type.CustomerAccountType"

headers = {
    "Content-Type": "application/json",
    "Connection": "keep-alive"
}

payload = {"limit": LIMIT, "offset": OFFSET, "filters": []}
params = {"sortFields": ["name"], "sortOrders": ["asc"]}

# Получаем клиентов из CRM
response = requests.get(
    URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers=headers,
    params=params,
    json=payload,
    timeout=10
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
def extract_contact_from_comment(comment: str) -> str | None:
    if not comment:
        return None

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

with CRM_TO_TG_FILE.open("w", encoding="utf-8") as f:
    json.dump(crm_to_tg, f, ensure_ascii=False, indent=2)
