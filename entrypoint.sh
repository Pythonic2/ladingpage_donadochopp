#!/bin/sh
set -eu

case "${RUN_MIGRATIONS:-false}" in
    true|True|TRUE|1|yes|Yes|YES)
        if [ "${DJANGO_ENV:-}" != "production" ]; then
            echo "ERROR: RUN_MIGRATIONS requires DJANGO_ENV=production." >&2
            exit 1
        fi
        python manage.py migrate --noinput
        ;;
esac

exec gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers "${GUNICORN_WORKERS:-1}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
