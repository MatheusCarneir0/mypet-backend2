import os
import django
from django.contrib.auth import get_user_model

# Setup Django environment (if running as standalone script, but we will run via shell)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

User = get_user_model()
email = 'admin@farmavet.com'
password = 'admin@123'
telefone = '88999999999'
nome = 'Administrador'

if not User.objects.filter(email=email).exists():
    try:
        User.objects.create_superuser(
            email=email,
            senha=password,
            nome=nome,
            telefone=telefone
        )
        print(f"Superuser {email} created successfully.")
    except Exception as e:
        print(f"Error creating superuser: {e}")
else:
    print(f"Superuser {email} already exists.")
