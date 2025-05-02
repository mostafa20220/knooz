#!/bin/sh
python manage.py migrate  --noinput
echo "database migrated"
python manage.py collectstatic --noinput
echo "static files collected"

# Check if arguments are passed
if [ -z "$1" ]; then
  echo "No command provided. Running default command..."
  ngrok-asgi gunicorn core.wsgi -b 0.0.0.0:8000 --disable-redirect-access-to-syslog --timeout 200  --workers=10 --threads=5 --worker-class=gthread --reload --domain "$NGROK_STATIC_DOMAIN"
else
  # Execute the passed command
  exec "$@"
fi