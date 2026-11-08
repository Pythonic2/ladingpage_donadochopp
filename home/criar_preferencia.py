import os

import mercadopago
from dotenv import load_dotenv


load_dotenv()


def env_or_default(name, default):
    return os.getenv(name) or default


BACK_URL_BASE = env_or_default(
    "MERCADO_PAGO_BACK_URL_BASE",
    "https://vendas.donadochopp.com.br",
)
NOTIFICATION_URL = env_or_default(
    "MERCADO_PAGO_NOTIFICATION_URL",
    "https://vendas.donadochopp.com.br/pag/",
)


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
        access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("MERCADO_PAGO_ACCESS_TOKEN não configurado")

        sdk = mercadopago.SDK(access_token)
        preference = sdk.preference().create(payload)
        if preference.get("status") in (200, 201):
            return preference.get("response")
        return preference.get("response") or preference
    except Exception as exc:
        print(f"Erro ao criar preferência no Mercado Pago: {exc}")
        return None
