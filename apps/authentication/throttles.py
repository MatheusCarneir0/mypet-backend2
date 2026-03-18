# apps/authentication/throttles.py
"""
Throttle classes customizadas para controle de taxa de requisições.
Protegem contra ataques de brute-force e spam de cadastros.
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limite por IP para tentativas de login.
    Configurado via THROTTLE_LOGIN_RATE (default: 5/minute).
    Evita ataques de força bruta em credenciais.
    """
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Limite por IP para criação de novas contas.
    Configurado via THROTTLE_REGISTER_RATE (default: 10/hour).
    Evita spam de cadastros.
    """
    scope = 'register'
