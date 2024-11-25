#!/bin/sh
python manage.py migrate  --noinput
echo "database migrated"
gunicorn core.wsgi -b 0.0.0.0:8000 --disable-redirect-access-to-syslog --timeout 200 --reload

