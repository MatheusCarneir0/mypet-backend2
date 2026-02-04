# apps/swagger/notificacoes.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.notificacoes.serializers import (
    NotificacaoSerializer,
    NotificacaoListSerializer
)

TAG = "Agendamentos"  # Notificações estão relacionadas a agendamentos

# Listagem
list_notificacoes = extend_schema(
    tags=[TAG],
    summary="Listar alertas",
    description="Retorna a lista de notificações/alertas do usuário autenticado. Clientes veem apenas notificações de seus agendamentos.",
    parameters=[
        OpenApiParameter(name='lida', description='Filtrar por status de leitura (true/false)', required=False, type=bool),
        OpenApiParameter(name='tipo', description='Filtrar por tipo de notificação', required=False, type=str),
    ],
    responses={200: envelop(NotificacaoListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_notificacao = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de uma notificação",
    description="Retorna os detalhes completos de uma notificação específica.",
    responses={
        200: envelop(NotificacaoSerializer),
        404: {"description": "Notificação não encontrada"}
    }
)

# Ações customizadas
marcar_lida = extend_schema(
    tags=[TAG],
    summary="Marcar como lida",
    description="Marca uma notificação como visualizada/lida pelo usuário.",
    responses={
        200: envelop(NotificacaoSerializer),
        404: {"description": "Notificação não encontrada"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
notificacao_view_schema = extend_schema_view(
    list=list_notificacoes,
    retrieve=retrieve_notificacao,
    read=marcar_lida,
)

