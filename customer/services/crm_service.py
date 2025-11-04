import requests
from requests.auth import HTTPBasicAuth

class CRMService:
    def __init__(self, layer_name: str, username: str, password: str, limit: int = 100, offset: int = 0):
        self.layer_name = layer_name
        self.base_url = f"https://{layer_name}.quickresto.ru/platform/online/api/list"
        self.auth = HTTPBasicAuth(username, password)
        self.limit = limit
        self.offset = offset
        self.headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }

    def get_customers(self):
        """Получение списка клиентов из CRM"""
        payload = {"limit": self.limit, "offset": self.offset, "filters": []}
        url = f"{self.base_url}?moduleName=crm.customer&className=ru.edgex.quickresto.modules.crm.customer.CrmCustomer"

        response = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка {response.status_code}: {response.text}")

        return response.json()

    def get_checks(self):
        """Получение списка чеков из CRM"""
        payload = {"limit": self.limit, "offset": self.offset, "filters": []}
        url = f"{self.base_url}?moduleName=front.orders&className=ru.edgex.quickresto.modules.front.orders.OrderInfo"

        response = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка {response.status_code}: {response.text}")

        return response.json()
