# apps/swagger/relatorios.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.relatorios.serializers import (
    RelatorioSerializer,
    RelatorioCreateSerializer
)

TAG = "Administração"

# Listagem
list_relatorios = extend_schema(
    tags=[TAG],
    summary="Listar relatórios",
    description="Retorna a lista de relatórios gerados. Apenas administradores podem acessar.",
    parameters=[
        OpenApiParameter(name='tipo', description='Filtrar por tipo de relatório', required=False, type=str),
        OpenApiParameter(name='formato', description='Filtrar por formato (PDF, XLSX)', required=False, type=str),
    ],
    responses={200: envelop(RelatorioSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_relatorio = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um relatório",
    description="Retorna os detalhes de um relatório específico.",
    responses={
        200: envelop(RelatorioSerializer),
        403: {"description": "Apenas administradores podem acessar"},
        404: {"description": "Relatório não encontrado"}
    }
)

# Criação
create_relatorio = extend_schema(
    tags=[TAG],
    summary="Gerar novo relatório",
    description="Gera um novo relatório com base nos filtros fornecidos. Apenas administradores podem gerar relatórios.",
    request=RelatorioCreateSerializer,
    responses={
        201: envelop(RelatorioSerializer),
        400: {"description": "Dados inválidos"},
        403: {"description": "Apenas administradores podem gerar relatórios"}
    }
)

# Ações customizadas
download_relatorio = extend_schema(
    tags=[TAG],
    summary="Download de relatório",
    description="Faz o download do arquivo de um relatório gerado.",
    responses={
        200: {"description": "Arquivo do relatório", "content": {"application/pdf": {}, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}}},
        404: {"description": "Relatório ou arquivo não encontrado"}
    }
)

dashboard_relatorios = extend_schema(
    tags=[TAG],
    summary="Obter dados do dashboard",
    description="Retorna dados agregados para o dashboard gerencial com KPIs (Faturamento, total de pets, etc) - UC26. Apenas administradores podem acessar.",
    responses={
        200: {
            "description": "Dados do dashboard",
            "type": "object",
            "properties": {
                "total_clientes": {"type": "integer"},
                "total_pets": {"type": "integer"},
                "total_agendamentos": {"type": "integer"},
                "receita_total": {"type": "number"},
                "agendamentos_hoje": {"type": "integer"},
                "agendamentos_mes": {"type": "integer"}
            }
        },
        403: {"description": "Apenas administradores podem acessar"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
relatorio_view_schema = extend_schema_view(
    list=list_relatorios,
    retrieve=retrieve_relatorio,
    create=create_relatorio,
    download=download_relatorio,
    dashboard=dashboard_relatorios,
)

