#!/bin/sh
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py seed_pagamentos
python manage.py shell -c "
from apps.authentication.models import Usuario
from django.contrib.auth.models import Group
admin, created = Usuario.objects.get_or_create(
    email='admin@farmavet.com',
    defaults={'nome': 'Administrador FarmaVet', 'telefone': '88999999999', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin.set_password('admin123')
    admin.save()
    group, _ = Group.objects.get_or_create(name='ADMINISTRADOR')
    admin.groups.add(group)
    print('Admin criado!')
else:
    print('Admin ja existe!')
"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 1 --threads 2