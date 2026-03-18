import os
import django
from django.contrib.auth import get_user_model

# Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

User = get_user_model()
exists = User.objects.filter(email='admin@farmavet.com').exists()

with open('verification_result.txt', 'w') as f:
    f.write(f"USER_EXISTS: {exists}")
print(f"USER_EXISTS: {exists}")
