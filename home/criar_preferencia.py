import os

import mercadopago
from dotenv import load_dotenv


load_dotenv()

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
IS_PRODUCTION = DJANGO_ENV == "production"


def env_or_default(name, default):
    return os.getenv(name) or default


ACCESS_TOKEN = os.getenv(
    "MERCADO_PAGO_ACCESS_TOKEN",
    
)
BACK_URL_BASE = env_or_default(
    "MERCADO_PAGO_BACK_URL_BASE",
    "https://vendas1.donadochopp.com.br" if IS_PRODUCTION else "http://127.0.0.1:8000",
)
NOTIFICATION_URL = env_or_default(
    "MERCADO_PAGO_NOTIFICATION_URL",
    "https://vendas1.donadochopp.com.br/pag/" if IS_PRODUCTION else "http://127.0.0.1:8000/pag/",
)

sdk = mercadopago.SDK(ACCESS_TOKEN)


def criar_preferencia(item: list, cliente_id: str):
    payload = {
        "items": item,
        "external_reference": cliente_id,
        "back_urls": {
            "failure": f"{BACK_URL_BASE}/falha/",
            "pending": f"{BACK_URL_BASE}/pendente/",
            "success": f"{BACK_URL_BASE}/sucesso/"
        },
        "notification_url": NOTIFICATION_URL
    }
    try:
        preference = sdk.preference().create(payload)
        if preference.get("status") in (200, 201):
            return preference.get("response")
        return preference.get("response") or preference
    except Exception as exc:
        print(f"Erro ao criar preferência no Mercado Pago: {exc}")
        return None
