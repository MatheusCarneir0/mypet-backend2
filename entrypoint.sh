#!/bin/sh
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
