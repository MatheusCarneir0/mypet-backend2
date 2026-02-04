# config/settings/development.py
from .base import *

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

# Email para console no desenvolvimento
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

