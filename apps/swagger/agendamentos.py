# apps/swagger/agendamentos.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.agendamentos.serializers import (
    AgendamentoDetailSerializer,
    AgendamentoListSerializer,
    AgendamentoCreateSerializer,
    AgendamentoUpdateSerializer,
    IniciarAgendamentoSerializer,
    ConcluirAgendamentoSerializer
)

TAG = "Agendamentos"

# Listagem
list_agendamentos = extend_schema(
    tags=[TAG],
    summary="Listar agendamentos",
    description="Retorna a lista de agendamentos com filtros de status e data. Clientes veem apenas seus agendamentos, funcionários veem os atribuídos a eles.",
    parameters=[
        OpenApiParameter(name='status', description='Filtrar por status', required=False, type=str),
        OpenApiParameter(name='data_inicio', description='Data de início (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='data_fim', description='Data de fim (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='pet', description='ID do pet', required=False, type=int),
        OpenApiParameter(name='servico', description='ID do serviço', required=False, type=int),
    ],
    responses={200: envelop(AgendamentoListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_agendamento = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um agendamento",
    description="Retorna os detalhes completos de um agendamento específico.",
    responses={
        200: envelop(AgendamentoDetailSerializer),
        404: {"description": "Agendamento não encontrado"}
    }
)

# Criação
create_agendamento = extend_schema(
    tags=[TAG],
    summary="Criar novo agendamento",
    description="Cria um novo agendamento para um pet e serviço com forma de pagamento (Frame 450). Apenas clientes podem criar agendamentos.",
    request=AgendamentoCreateSerializer,
    responses={
        201: envelop(AgendamentoDetailSerializer),
        400: {"description": "Dados inválidos ou conflito de horário"}
    }
)

# Nota: PUT e DELETE foram desativados - use apenas as ações customizadas (cancelar, reagendar, iniciar, concluir)

# Ações customizadas
cancelar_agendamento = extend_schema(
    tags=[TAG],
    summary="Cancelar agendamento",
    description="Cancela um agendamento existente alterando status para CANCELADO (Frame 467). Clientes podem cancelar seus próprios agendamentos.",
    request={
        "type": "object",
        "properties": {
            "motivo": {"type": "string", "description": "Motivo do cancelamento"}
        }
    },
    responses={
        200: envelop({"type": "object", "properties": {"message": {"type": "string"}}}),
        400: {"description": "Agendamento não pode ser cancelado"},
        404: {"description": "Agendamento não encontrado"}
    }
)

reagendar_agendamento = extend_schema(
    tags=[TAG],
    summary="Reagendar um agendamento",
    description="Reagenda um agendamento para uma nova data/hora.",
    request={
        "type": "object",
        "properties": {
            "data_hora": {"type": "string", "format": "date-time", "description": "Nova data e hora do agendamento"}
        },
        "required": ["data_hora"]
    },
    responses={
        200: {"description": "Agendamento reagendado com sucesso"},
        400: {"description": "Data/hora inválida ou conflito de horário"},
        404: {"description": "Agendamento não encontrado"}
    }
)

iniciar_agendamento = extend_schema(
    tags=[TAG],
    summary="Iniciar serviço",
    description="Inicia um agendamento alterando status para EM_ANDAMENTO (apenas funcionários).",
    request=IniciarAgendamentoSerializer,
    responses={
        200: envelop({"type": "object", "properties": {"message": {"type": "string"}}}),
        400: {"description": "Agendamento não pode ser iniciado"},
        404: {"description": "Agendamento não encontrado"}
    }
)

concluir_agendamento = extend_schema(
    tags=[TAG],
    summary="Concluir agendamento",
    description="Finaliza o serviço, registra pagamento e gera histórico (apenas funcionários).",
    request=ConcluirAgendamentoSerializer,
    responses={
        200: envelop({"type": "object", "properties": {"message": {"type": "string"}}}),
        400: {"description": "Agendamento não pode ser concluído"},
        404: {"description": "Agendamento não encontrado"}
    }
)

horarios_disponiveis = extend_schema(
    tags=[TAG],
    summary="Consultar horários disponíveis",
    description="Retorna os horários livres por data e serviço (Frame 440).",
    parameters=[
        OpenApiParameter(name='data', description='Data no formato YYYY-MM-DD', required=True, type=str),
        OpenApiParameter(name='servico_id', description='ID do serviço', required=True, type=int),
    ],
    responses={
        200: envelop({
            "type": "array",
            "items": {"type": "string", "format": "time"}
        }),
        400: {"description": "Parâmetros inválidos"}
    }
)

atualizar_status_agendamento = extend_schema(
    tags=[TAG],
    summary="Iniciar serviço",
    description="Inicia o serviço alterando status para EM_ANDAMENTO (apenas funcionários).",
    request={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["AGENDADO", "CONFIRMADO", "EM_ANDAMENTO", "CONCLUIDO", "CANCELADO", "NAO_COMPARECEU"],
                "description": "Novo status do agendamento"
            }
        },
        "required": ["status"]
    },
    responses={
        200: envelop(AgendamentoDetailSerializer),
        400: {"description": "Status inválido ou transição não permitida"},
        404: {"description": "Agendamento não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
agendamento_view_schema = extend_schema_view(
    list=list_agendamentos,
    retrieve=retrieve_agendamento,
    create=create_agendamento,
    cancelar=cancelar_agendamento,
    reagendar=reagendar_agendamento,
    iniciar=iniciar_agendamento,
    concluir=concluir_agendamento,
    horarios_disponiveis=horarios_disponiveis,
    disponibilidade=horarios_disponiveis,
    status=atualizar_status_agendamento,
)
