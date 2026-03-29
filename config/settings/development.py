
# config/settings/development.py
from .base import *
import os

# Storage local para desenvolvimento
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEBUG = True

# Apenas adiciona apps de desenvolvimento se estiverem instalados
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
except ImportError:
    pass

INTERNAL_IPS = [
    '127.0.0.1',
]

# O backend de email será gerenciado pelo base.py (lendo do .env)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}