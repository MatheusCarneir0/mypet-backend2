# apps/swagger/historico.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.historico.serializers import (
    HistoricoAtendimentoSerializer,
    HistoricoAtendimentoListSerializer
)

TAG = "Histórico"  # Histórico separado de Pets

# Listagem
list_historico = extend_schema(
    tags=[TAG],
    summary="Listar histórico de atendimentos",
    description="Retorna o histórico de atendimentos concluídos. Clientes veem apenas histórico de seus pets.",
    parameters=[
        OpenApiParameter(name='pet', description='Filtrar por ID do pet', required=False, type=int),
        OpenApiParameter(name='data_inicio', description='Data de início (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='data_fim', description='Data de fim (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='ordering', description='Ordenar por data_atendimento ou valor_pago', required=False, type=str),
    ],
    responses={200: envelop(HistoricoAtendimentoListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_historico = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um atendimento histórico",
    description="Retorna os detalhes completos de um atendimento específico do histórico.",
    responses={
        200: envelop(HistoricoAtendimentoSerializer),
        404: {"description": "Atendimento não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
historico_view_schema = extend_schema_view(
    list=list_historico,
    retrieve=retrieve_historico,
)

