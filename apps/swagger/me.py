# apps/swagger/me.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.authentication.serializers import (
    UsuarioSerializer,
    AlterarSenhaSerializer,
    UploadFotoSerializer
)

TAG = "Perfil"

# Perfil
perfil_retrieve = extend_schema(
    tags=[TAG],
    summary="Ver meu perfil",
    description="Retorna os dados do usuário logado (Frame 437).",
    responses={
        200: envelop(UsuarioSerializer),
        401: {"description": "Não autenticado"}
    }
)

perfil_update = extend_schema(
    tags=[TAG],
    summary="Atualizar meu perfil",
    description="Atualiza os dados cadastrais do usuário autenticado (Frame 437).",
    request=UsuarioSerializer,
    responses={
        200: envelop(UsuarioSerializer),
        400: {"description": "Dados inválidos"},
        401: {"description": "Não autenticado"}
    }
)

# Upload de Foto
upload_foto = extend_schema(
    tags=[TAG],
    summary="Enviar foto de perfil",
    description="Faz upload de foto de perfil do usuário autenticado (Frame 437).",
    request=UploadFotoSerializer,
    responses={
        200: envelop(UsuarioSerializer),
        400: {"description": "Arquivo inválido"},
        401: {"description": "Não autenticado"}
    }
)

# Alterar senha
alterar_senha = extend_schema(
    tags=[TAG],
    summary="Alterar senha",
    description="Altera a senha do usuário autenticado.",
    request=AlterarSenhaSerializer,
    responses={
        200: {"description": "Senha alterada com sucesso"},
        400: {"description": "Dados inválidos ou senha atual incorreta"},
        401: {"description": "Não autenticado"}
    }
)

# Schema view para PerfilView
perfil_view_schema = extend_schema_view(
    get=perfil_retrieve,
    put=perfil_update,
    patch=perfil_update,
)

