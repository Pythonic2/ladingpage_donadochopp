import requests

import requests

def criar_preferencia(item: list, cliente_id: str):
    api_token = "TEST-7847881527057924-091116-0ccb25f4e7a8318b77ae79bcb1f4c205-162016798"
    url = f"https://api_gateway.gestcloud.com.br/api/v1/preferences/create-preference/{api_token}/"

    payload = {
        "items": item,
        "client_id": cliente_id,
        "back_urls": {
            "failure": "https://www.seusite.com/falha/",
            "pending": "https://www.seusite.com/pendente/",
            "success": "https://www.seusite.com/sucesso/"
        },
        "notification_url": "https://vendas.donadochopp.com.br/notificacao/"
    }

    response = requests.post(url, json=payload, verify=False)
    try:
        return response.json()
    except Exception:
        return None