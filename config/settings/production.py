# config/settings/production.py
from .base import *
from decouple import config

DEBUG = False

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS — força HTTPS por 1 ano (habilitar somente após configurar certificado SSL)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS em produção — obrigatório configurar via variável de ambiente CORS_ORIGINS
# Exemplo: CORS_ORIGINS=https://mypet.com.br,https://www.mypet.com.br
_cors_prod = config('CORS_ORIGINS', default='')
if _cors_prod:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_prod.split(',') if o.strip()]

# Sentry para monitoramento de erros em produção
if config('SENTRY_DSN', default=None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.2,   # 20% de sample em produção (economizar cota)
        send_default_pii=False,   # LGPD: não enviar dados pessoais ao Sentry
    )
