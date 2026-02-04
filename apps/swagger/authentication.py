# apps/swagger/authentication.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.authentication.serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
    AlterarSenhaSerializer,
    GoogleLoginSerializer,
    UploadFotoSerializer
)

TAG = "Autenticação"

# Token
obter_token = extend_schema(
    tags=[TAG],
    summary="Login",
    description="Autentica o usuário e retorna tokens JWT (access e refresh).",
    request=CustomTokenObtainPairSerializer,
    responses={
        200: envelop(CustomTokenObtainPairSerializer),
        401: {"description": "Credenciais inválidas"}
    }
)

refresh_token = extend_schema(
    tags=[TAG],
    summary="Renovar token",
    description="Renova o token de acesso usando o refresh token.",
    responses={
        200: {"description": "Novo token de acesso gerado"},
        401: {"description": "Refresh token inválido ou expirado"}
    }
)

# Registro
registro = extend_schema(
    tags=[TAG],
    summary="Auto-cadastro",
    description="Cria uma nova conta de cliente no sistema (auto-cadastro).",
    request=UsuarioCreateSerializer,
    responses={
        201: envelop(UsuarioSerializer),
        400: {"description": "Dados inválidos"}
    }
)

# Login Social
google_login = extend_schema(
    tags=[TAG],
    summary="Login com Google",
    description="Autentica ou cria usuário via Google OAuth (Frame 429).",
    request=GoogleLoginSerializer,
    responses={
        200: envelop(CustomTokenObtainPairSerializer),
        400: {"description": "Dados inválidos ou token inválido"}
    }
)

