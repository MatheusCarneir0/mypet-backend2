# apps/swagger/pagamentos.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.pagamentos.serializers import (
    FormaPagamentoSerializer,
    TransacaoPagamentoSerializer,
    ProcessarPagamentoDinheiroSerializer,
    ProcessarPagamentoCartaoSerializer,
    ProcessarPagamentoPixSerializer,
    ConfirmarPagamentoPixSerializer
)

TAG_PAGAMENTOS = "Financeiro"
TAG_FORMAS_PAGAMENTO = "Administração"  # CRUD de formas de pagamento é administrativo

# Formas de Pagamento (somente leitura para clientes)
list_formas_pagamento = extend_schema(
    tags=[TAG_PAGAMENTOS],  # Listagem pública é financeiro
    summary="Listar formas de pagamento",
    description="Retorna a lista de formas de pagamento disponíveis no sistema.",
    responses={200: envelop(FormaPagamentoSerializer(many=True), paginated=True)}
)

retrieve_forma_pagamento = extend_schema(
    tags=[TAG_PAGAMENTOS],  # Formas de pagamento são financeiro
    summary="Obter detalhes de uma forma de pagamento",
    description="Retorna os detalhes de uma forma de pagamento específica.",
    responses={
        200: envelop(FormaPagamentoSerializer),
        404: {"description": "Forma de pagamento não encontrada"}
    }
)

# Transações de Pagamento
list_transacoes = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Listar transações de pagamento",
    description="Retorna a lista de transações de pagamento.",
    parameters=[
        OpenApiParameter(name='agendamento', description='Filtrar por ID do agendamento', required=False, type=int),
        OpenApiParameter(name='status', description='Filtrar por status', required=False, type=str),
    ],
    responses={200: envelop(TransacaoPagamentoSerializer(many=True), paginated=True)}
)

retrieve_transacao = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Obter detalhes de uma transação",
    description="Retorna os detalhes completos de uma transação de pagamento específica.",
    responses={
        200: envelop(TransacaoPagamentoSerializer),
        404: {"description": "Transação não encontrada"}
    }
)

# Processar Pagamentos
processar_dinheiro = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Processar pagamento em dinheiro",
    description="Processa um pagamento em dinheiro para um agendamento concluído.",
    request=ProcessarPagamentoDinheiroSerializer,
    responses={
        201: envelop(TransacaoPagamentoSerializer),
        400: {"description": "Dados inválidos ou agendamento não pode ser pago"}
    }
)

processar_cartao = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Processar pagamento com cartão",
    description="Processa um pagamento com cartão de crédito/débito para um agendamento concluído.",
    request=ProcessarPagamentoCartaoSerializer,
    responses={
        201: envelop(TransacaoPagamentoSerializer),
        400: {"description": "Dados inválidos ou agendamento não pode ser pago"}
    }
)

gerar_pix = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Gerar pagamento PIX",
    description="Gera QR Code e código PIX para pagamento de um agendamento concluído.",
    request=ProcessarPagamentoPixSerializer,
    responses={
        201: envelop(TransacaoPagamentoSerializer),
        400: {"description": "Dados inválidos ou agendamento não pode ser pago"}
    }
)

confirmar_pix = extend_schema(
    tags=[TAG_PAGAMENTOS],
    summary="Confirmar pagamento PIX",
    description="Confirma o recebimento de um pagamento PIX após verificação manual.",
    request=ConfirmarPagamentoPixSerializer,
    responses={
        200: envelop(TransacaoPagamentoSerializer),
        400: {"description": "Dados inválidos ou transação não pode ser confirmada"},
        404: {"description": "Transação não encontrada"}
    }
)

# Schema views para aplicar todos os decorators de uma vez
forma_pagamento_view_schema = extend_schema_view(
    list=list_formas_pagamento,
    retrieve=retrieve_forma_pagamento,
)

transacao_pagamento_view_schema = extend_schema_view(
    list=list_transacoes,
    retrieve=retrieve_transacao,
    processar_dinheiro=processar_dinheiro,
    processar_cartao=processar_cartao,
    gerar_pix=gerar_pix,
    confirmar_pix=confirmar_pix,
)

