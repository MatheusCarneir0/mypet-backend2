# apps/swagger/clientes.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.clientes.serializers import (
    ClienteDetailSerializer,
    ClienteListSerializer,
    ClienteCreateSerializer,
    ClienteUpdateSerializer,
)

TAG = "Clientes"

# Listagem
list_clientes = extend_schema(
    tags=[TAG],
    summary="Listar clientes",
    description="Retorna a lista geral de clientes cadastrados. Acesso restrito a Admin/Funcionário.",
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nome, email, CPF ou cidade', required=False, type=str),
        OpenApiParameter(name='cidade', description='Filtrar por cidade', required=False, type=str),
        OpenApiParameter(name='estado', description='Filtrar por estado', required=False, type=str),
    ],
    responses={200: envelop(ClienteListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_cliente = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um cliente",
    description="Retorna os detalhes completos de um cliente específico.",
    responses={
        200: envelop(ClienteDetailSerializer),
        404: {"description": "Cliente não encontrado"}
    }
)


# Deleção (Soft Delete)
destroy_cliente = extend_schema(
    tags=[TAG],
    summary="Deletar cliente (soft delete)",
    description="Desativa um cliente (soft delete). Apenas administradores podem executar esta ação.",
    responses={
        204: {"description": "Cliente deletado com sucesso"},
        403: {"description": "Sem permissão para deletar"},
        404: {"description": "Cliente não encontrado"}
    }
)

# Criação
create_cliente = extend_schema(
    tags=[TAG],
    summary="Criar novo cliente",
    description="Cria um novo cliente no sistema. Acesso restrito a Admin/Funcionário.",
    request=ClienteCreateSerializer,
    responses={
        201: envelop(ClienteDetailSerializer),
        400: {"description": "Dados inválidos"}
    }
)

# Atualização
update_cliente = extend_schema(
    tags=[TAG],
    summary="Atualizar cliente",
    description="Atualiza os dados de um cliente existente.",
    request=ClienteUpdateSerializer,
    responses={
        200: envelop(ClienteDetailSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Cliente não encontrado"}
    }
)

partial_update_cliente = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente um cliente",
    description="Atualiza parcialmente os dados de um cliente existente.",
    request=ClienteUpdateSerializer,
    responses={
        200: envelop(ClienteDetailSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Cliente não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
cliente_view_schema = extend_schema_view(
    list=list_clientes,
    retrieve=retrieve_cliente,
    create=create_cliente,
    update=update_cliente,
    partial_update=partial_update_cliente,
    destroy=destroy_cliente,
)

