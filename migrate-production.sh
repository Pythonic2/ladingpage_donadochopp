#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ENV="${PROJECT_ROOT}/.env"
COMERCIAL_ENV="${COMERCIAL_ENV:-${PROJECT_ROOT}/../comercial_tool/.env}"
PYTHON_BIN="${PYTHON_BIN:-${PROJECT_ROOT}/venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
if [ -z "$PYTHON_BIN" ]; then
  echo "Erro: Python não encontrado." >&2
  exit 1
fi

"$PYTHON_BIN" - "$COMERCIAL_ENV" "$APP_ENV" "$PROJECT_ROOT" <<'PY'
import os
import subprocess
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


commercial_env, app_env, project_root = sys.argv[1:]
env = os.environ.copy()
env.update(read_env(commercial_env))
env.update(read_env(app_env))
env.update(
    {
        "DJANGO_ENV": "production",
        "DB_SCHEMA": "ladingpageddc",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
)

code = """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('CREATE SCHEMA IF NOT EXISTS ladingpageddc')
print('Schema ladingpageddc pronto.')
"""
subprocess.run([sys.executable, "-c", code], cwd=project_root, env=env, check=True)
subprocess.run(
    [sys.executable, "manage.py", "migrate", "--noinput"],
    cwd=project_root,
    env=env,
    check=True,
)
PY

