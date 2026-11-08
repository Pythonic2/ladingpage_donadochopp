#!/usr/bin/env bash
set -euo pipefail

SERVICE="${SERVICE:-landingpage-donadochopp}"
REGION="${REGION:-southamerica-east1}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ENV="${PROJECT_ROOT}/.env"
COMERCIAL_ENV="${COMERCIAL_ENV:-${PROJECT_ROOT}/../comercial_tool/.env}"

command -v gcloud >/dev/null || {
  echo "Erro: gcloud não está disponível no PATH." >&2
  exit 1
}
command -v python3 >/dev/null || {
  echo "Erro: python3 não está disponível no PATH." >&2
  exit 1
}

for env_file in "$APP_ENV" "$COMERCIAL_ENV"; do
  if [ ! -f "$env_file" ]; then
    echo "Erro: arquivo não encontrado: $env_file" >&2
    exit 1
  fi
done

TEMP_ENV="$(mktemp "${TMPDIR:-/tmp}/landingpage-cloud-run-env.XXXXXX.json")"
trap 'rm -f "$TEMP_ENV"' EXIT

python3 - "$COMERCIAL_ENV" "$APP_ENV" "$TEMP_ENV" <<'PY'
import json
import sys
from pathlib import Path


def read_env(path):
    values = {}
    for raw_line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


commercial = read_env(sys.argv[1])
app = read_env(sys.argv[2])

db_keys = {
    "SECRET_KEY",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_SSLMODE",
    "DB_CHANNEL_BINDING",
    "DB_CONNECT_TIMEOUT",
    "DB_CONN_MAX_AGE",
}
merged = {key: value for key, value in commercial.items() if key in db_keys}
merged.update(app)
merged.update(
    {
        "DJANGO_ENV": "production",
        "DEBUG": "false",
        "DB_SCHEMA": "ladingpageddc",
        "SERVE_MEDIA": "false",
        "RUN_MIGRATIONS": "false",
        "GCS_ENABLED": "true",
        "GCS_BUCKET_NAME": "gesttechmidias",
        "GCS_PROJECT_ID": "gestcloud-500200",
        "GCS_APP_PREFIX": "landing-page-ddc",
        "GCS_IAM_SIGN_BLOB": "true",
        "GCS_SA_EMAIL": "926822874156-compute@developer.gserviceaccount.com",
        "GCS_SIGNED_URL_TTL": "604800",
        "GCS_SIGNED_URL_CACHE_TTL": "604500",
    }
)
merged.setdefault("ALLOWED_HOSTS", ".run.app,vendas.donadochopp.com.br")
merged.setdefault(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.run.app,https://vendas.donadochopp.com.br",
)

required = (
    "SECRET_KEY",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "MERCADO_PAGO_ACCESS_TOKEN",
)
missing = [key for key in required if not merged.get(key)]
if missing:
    raise SystemExit("Variáveis obrigatórias ausentes: " + ", ".join(missing))

Path(sys.argv[3]).write_text(json.dumps(merged), encoding="utf-8")
PY

gcloud run deploy "$SERVICE" \
  --source "$PROJECT_ROOT" \
  --region "$REGION" \
  --service-account "926822874156-compute@developer.gserviceaccount.com" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1 \
  --concurrency 20 \
  --set-env-vars-file "$TEMP_ENV"

