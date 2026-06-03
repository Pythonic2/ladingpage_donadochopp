import requests


ACCESS_TOKEN = "APP_USR-1593410664899051-060316-fd084459c24e48c1e48398ad93781783-3449228666"
MERCADO_PAGO_PREFERENCE_URL = "https://api.mercadopago.com/checkout/preferences"


def criar_preferencia(item: list, cliente_id: str):
    payload = {
        "items": item,
        "external_reference": cliente_id,
        "back_urls": {
            "failure": "https://vendas1.donadochopp.com.br/falha/",
            "pending": "https://vendas1.donadochopp.com.br/pendente/",
            "success": "https://vendas1.donadochopp.com.br/sucesso/"
        },
        "notification_url": "http://localhost:8000/pag/"
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        MERCADO_PAGO_PREFERENCE_URL,
        json=payload,
        headers=headers,
        timeout=20,
    )
    try:
        return response.json()
    except Exception:
        return None
