# apps/swagger/clientes.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.clientes.serializers import (
    ClienteDetailSerializer,
    ClienteListSerializer,
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

# Schema view para aplicar todos os decorators de uma vez
# IMPORTANTE: Apenas list, retrieve e destroy estão habilitados
# create, update e partial_update foram BLOQUEADOS (ver http_method_names)
cliente_view_schema = extend_schema_view(
    list=list_clientes,
    retrieve=retrieve_cliente,
    destroy=destroy_cliente,
)

