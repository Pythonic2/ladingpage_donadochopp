#!/bin/sh
# Aplica migrações antes de iniciar o servidor
echo "Rodando makemigrations e migrate..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Inicia o Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
