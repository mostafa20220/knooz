#!/bin/sh
python manage.py migrate  --noinput
echo "database migrated"
python manage.py collectstatic --noinput
echo "static files collected"
gunicorn core.wsgi -b 0.0.0.0:8000 --disable-redirect-access-to-syslog --timeout 200 --reload

