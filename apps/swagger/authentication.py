# apps/swagger/authentication.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.authentication.serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
    AlterarSenhaSerializer,
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

# Usuário (Actions do UserViewSet)
me = extend_schema(
    tags=[TAG],
    summary="Ver meu perfil",
    description="Retorna os dados do usuário autenticado.",
    responses={200: envelop(UsuarioSerializer)}
)

alterar_senha = extend_schema(
    tags=[TAG],
    summary="Alterar senha",
    description="Altera a senha do usuário autenticado.",
    request=AlterarSenhaSerializer,
    responses={
        200: {"description": "Senha alterada com sucesso"},
        400: {"description": "Dados inválidos ou senha atual incorreta"}
    }
)

upload_foto = extend_schema(
    tags=[TAG],
    summary="Upload de foto de perfil",
    description="Faz o upload ou atualiza a foto de perfil do usuário.",
    request=UploadFotoSerializer,
    responses={
        200: {"description": "Foto atualizada com sucesso"},
        400: {"description": "Erro no upload"}
    }
)

# Schema View para o UserViewSet (se necessário agrupar)
usuario_view_schema = extend_schema_view(
    me=me,
    alterar_senha=alterar_senha,
    upload_foto=upload_foto
)

