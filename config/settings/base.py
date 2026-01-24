# User Model Customizado
AUTH_USER_MODEL = 'users.User'  # CRÍTICO: deve estar ANTES de INSTALLED_APPS

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',  
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    
    # Local apps - ORDEM IMPORTA!
    'apps.users',  # PRIMEIRO (dependência dos outros)
    'apps.clients',
    'apps.employees',
    'apps.pets',
    'apps.services',
    'apps.appointments',
    'apps.payments',
    'apps.notifications',
    'core',
]