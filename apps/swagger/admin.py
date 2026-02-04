# apps/swagger/admin.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.relatorios.serializers import (
    RelatorioSerializer,
    RelatorioCreateSerializer
)
from apps.pagamentos.serializers import FormaPagamentoSerializer

TAG = "Administração"

dashboard = extend_schema(
    tags=[TAG],
    summary="Dashboard gerencial",
    description="Retorna métricas gerenciais (Faturamento, total de pets, etc) - UC26. Apenas administradores podem acessar.",
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

gerar_relatorio = extend_schema(
    tags=[TAG],
    summary="Gerar relatório",
    description="Gera PDF/Excel de Serviços, Faturamento ou Clientes com base nos filtros fornecidos. Apenas administradores podem gerar relatórios.",
    request=RelatorioCreateSerializer,
    responses={
        201: envelop(RelatorioSerializer),
        400: {"description": "Dados inválidos"},
        403: {"description": "Apenas administradores podem gerar relatórios"}
    }
)

# Formas de Pagamento (Admin CRUD)
list_formas_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Listar formas de pagamento (Admin)",
    description="Lista todas as formas de pagamento. Apenas administradores.",
    responses={200: envelop(FormaPagamentoSerializer(many=True), paginated=True)}
)

retrieve_forma_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Obter forma de pagamento (Admin)",
    description="Retorna detalhes de uma forma de pagamento. Apenas administradores.",
    responses={
        200: envelop(FormaPagamentoSerializer),
        404: {"description": "Forma de pagamento não encontrada"}
    }
)

create_forma_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Criar forma de pagamento (Admin)",
    description="Cria uma nova forma de pagamento. Apenas administradores.",
    request=FormaPagamentoSerializer,
    responses={
        201: envelop(FormaPagamentoSerializer),
        400: {"description": "Dados inválidos"}
    }
)

update_forma_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Atualizar forma de pagamento (Admin)",
    description="Atualiza uma forma de pagamento. Apenas administradores.",
    request=FormaPagamentoSerializer,
    responses={
        200: envelop(FormaPagamentoSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Forma de pagamento não encontrada"}
    }
)

partial_update_forma_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente forma de pagamento (Admin)",
    description="Atualiza parcialmente uma forma de pagamento. Apenas administradores.",
    request=FormaPagamentoSerializer,
    responses={
        200: envelop(FormaPagamentoSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Forma de pagamento não encontrada"}
    }
)

destroy_forma_pagamento_admin = extend_schema(
    tags=[TAG],
    summary="Excluir forma de pagamento (Admin)",
    description="Exclui (desativa) uma forma de pagamento. Apenas administradores.",
    responses={
        204: {"description": "Forma de pagamento excluída com sucesso"},
        404: {"description": "Forma de pagamento não encontrada"}
    }
)

# Schema views para aplicar todos os decorators de uma vez
admin_forma_pagamento_view_schema = extend_schema_view(
    list=list_formas_pagamento_admin,
    retrieve=retrieve_forma_pagamento_admin,
    create=create_forma_pagamento_admin,
    update=update_forma_pagamento_admin,
    partial_update=partial_update_forma_pagamento_admin,
    destroy=destroy_forma_pagamento_admin,
)

