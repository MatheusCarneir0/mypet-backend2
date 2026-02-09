import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = 'admin@farmavet.com'
password = 'admin@123'

try:
    user = User.objects.get(email=email)
    print(f"User found: {user.email}")
    
    # Ensure flags
    user.is_staff = True
    user.is_superuser = True
    user.ativo = True
    
    # Force password set
    user.set_password(password)
    user.save()
    
    print(f"User updated successfully.")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_superuser: {user.is_superuser}")
    print(f"ativo: {user.ativo}")
    print(f"is_active (property): {user.is_active}")

except User.DoesNotExist:
    print(f"User {email} does not exist. Creating...")
    User.objects.create_superuser(
        email=email,
        senha=password,
        nome='Admin',
        telefone='88999999999'
    )
    print("User created.")
except Exception as e:
    print(f"Error: {e}")
