# apps/authentication/apps.py
"""
Configuração do app authentication.
"""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticação'
    
    def ready(self):
        """
        Importa signals quando o app está pronto.
        """
        import apps.authentication.signals  # noqa
