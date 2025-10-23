import requests
from requests.auth import HTTPBasicAuth
from core.paths import CONFIG
import json

class CRMClient:
    def __init__(self, layer_name, username, password):
        self.base = f"https://{layer_name}.quickresto.ru"
        self.auth = HTTPBasicAuth(username, password)

    def fetch_orders(self, limit=100, offset=0):
        url = f"{self.base}/platform/online/api/list"
        params = {"moduleName":"front.orders","className":"ru.edgex.quickresto.modules.front.orders.OrderInfo"}
        payload = {"limit": limit, "offset": offset, "filters": []}
        r = requests.get(url, auth=self.auth, params=params, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
