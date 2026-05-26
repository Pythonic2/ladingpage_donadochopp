#!/bin/sh
set -e

echo "Preparando diretórios..."
mkdir -p /app/media

echo "Rodando makemigrations e migrate..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

exec gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8010}
