import requests

import requests

def criar_preferencia(item: list, cliente_id: str):
    api_token = "APP_USR-7550924195079584-082016-1c30a22b4758afcd630361ba8b415c1b-718297245"
    url = f"https://api_gateway.gestcloud.com.br/api/v1/preferences/create-preference/{api_token}/"
    #fgsgesf
    payload = {
        "items": item,
        "client_id": cliente_id,
        "back_urls": {
            "failure": "https://vendas.donadochopp.com.br/falha/",
            "pending": "https://vendas.donadochopp.com.br/pendente/",
            "success": "https://vendas.donadochopp.com.br/sucesso/"
        },
        "notification_url": "https://vendas.donadochopp.com.br/pag/"
    }

    response = requests.post(url, json=payload, verify=False)
    try:
        return response.json()
    except Exception:
        return None