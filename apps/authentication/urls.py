# apps/authentication/urls.py
"""
URLs para autenticação.
Agrupa: Login (JWT), Registro de Clientes, Google Login e Refresh Token.
"""
from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    RegistroView,
    GoogleLoginView,
)

app_name = 'authentication'

urlpatterns = [
    # Autenticação JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refresh'),
    
    # Registro de Clientes
    path('register/', RegistroView.as_view(), name='register'),
    
    # Login Social
    path('google/', GoogleLoginView.as_view(), name='google'),
]

