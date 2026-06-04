#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import mercadopago
from dotenv import load_dotenv
from mercadopago.config import RequestOptions


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta um pagamento no Mercado Pago usando MERCADO_PAGO_ACCESS_TOKEN."
    )
    parser.add_argument("payment_id", help="ID do pagamento/transação no Mercado Pago")
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("MERCADO_PAGO_PAYMENT_TIMEOUT", "20.0")),
        help="Timeout de conexão em segundos",
    )
    args = parser.parse_args()

    access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
    if not access_token:
        raise SystemExit("MERCADO_PAGO_ACCESS_TOKEN não encontrado no ambiente/.env")

    sdk = mercadopago.SDK(access_token)
    request_options = RequestOptions(
        connection_timeout=args.timeout,
        max_retries=int(os.getenv("MERCADO_PAGO_PAYMENT_RETRIES", "1")),
    )

    response = sdk.payment().get(args.payment_id, request_options=request_options)
    print(json.dumps(response, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
