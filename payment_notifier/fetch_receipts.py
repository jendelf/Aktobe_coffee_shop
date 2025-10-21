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

URL = f"https://{LAYER_NAME}.quickresto.ru/platform/online/api/list?moduleName=front.orders&className=ru.edgex.quickresto.modules.front.orders.OrderInfo"

headers = {
    "Content-Type": "application/json",
    "Connection": "keep-alive"
}

payload = {"limit": LIMIT, "offset": OFFSET, "filters": []}
params = {"sortFields": ["name"], "sortOrders": ["asc"]}

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

receipts = response.json()

with open("receipts.json", "w", encoding="utf-8") as f:
    json.dump(receipts, f, ensure_ascii=False, indent=4)
print("Чеки успешно сохранены")

