import requests

import requests

def criar_preferencia(item: list, cliente_id: str):
    api_token = "TEST-654382218469227-040219-8e0ed7a2863e1f4d290cd4297285598c-718297245"
    url = f"https://api_gateway.gestcloud.com.br/api/v1/preferences/create-preference/{api_token}/"

    payload = {
        "items": item,
        "client_id": cliente_id,
        "notification_url": "https://vendas.donadochopp.com.br/pag/"
    }

    response = requests.post(url, json=payload, verify=False)
    try:
        return response.json()
    except Exception:
        return None