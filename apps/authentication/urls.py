# apps/authentication/urls.py
"""
URLs para autenticação.
Agrupa: Login (JWT), Registro de Clientes e Refresh Token.
"""
from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    RegistroView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

app_name = 'authentication'

urlpatterns = [
    # Autenticação JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refresh'),

    # Registro de Clientes
    path('register/', RegistroView.as_view(), name='register'),

    # Recuperação de Senha
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

