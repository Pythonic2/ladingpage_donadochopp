import requests

import requests

def criar_preferencia(item: list, cliente_id: str):
    api_token = "TEST-2561083729574154-071410-35c6aae2d12d09d5a84f429d5fb0d6bc-162016798"
    url = f"https://api_gateway.gestcloud.com.br/api/v1/preferences/create-preference/{api_token}/"

    payload = {
        "items": item,
        "client_id": cliente_id
    }

    response = requests.post(url, json=payload, verify=False)
    try:
        return response.json()
    except Exception:
        return None