# apps/swagger/funcionarios.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.funcionarios.serializers import (
    FuncionarioSerializer,
    FuncionarioListSerializer,
    FuncionarioCreateSerializer,
    FuncionarioUpdateSerializer,
    HorarioTrabalhoSerializer,
)

TAG = "Funcionários"

# Listagem
list_funcionarios = extend_schema(
    tags=[TAG],
    summary="Listar funcionários",
    description="Retorna a lista de funcionários cadastrados com gestão de equipe e horários. Apenas administradores podem acessar.",
    responses={200: envelop(FuncionarioListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_funcionario = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um funcionário",
    description="Retorna os detalhes completos de um funcionário específico.",
    responses={
        200: envelop(FuncionarioSerializer),
        403: {"description": "Apenas administradores podem acessar"},
        404: {"description": "Funcionário não encontrado"}
    }
)

# Criação
create_funcionario = extend_schema(
    tags=[TAG],
    summary="Criar novo funcionário",
    description="Cria um novo funcionário no sistema. Apenas administradores podem criar funcionários.",
    request=FuncionarioCreateSerializer,
    responses={
        201: envelop(FuncionarioSerializer),
        400: {"description": "Dados inválidos"},
        403: {"description": "Apenas administradores podem criar funcionários"}
    }
)

# Atualização
update_funcionario = extend_schema(
    tags=[TAG],
    summary="Atualizar funcionário",
    description="Atualiza os dados de um funcionário existente.",
    request=FuncionarioUpdateSerializer,
    responses={
        200: envelop(FuncionarioSerializer),
        400: {"description": "Dados inválidos"},
        403: {"description": "Apenas administradores podem atualizar"},
        404: {"description": "Funcionário não encontrado"}
    }
)

partial_update_funcionario = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente um funcionário",
    description="Atualiza parcialmente os dados de um funcionário existente.",
    request=FuncionarioUpdateSerializer,
    responses={
        200: envelop(FuncionarioSerializer),
        400: {"description": "Dados inválidos"},
        403: {"description": "Apenas administradores podem atualizar"},
        404: {"description": "Funcionário não encontrado"}
    }
)

# Exclusão
destroy_funcionario = extend_schema(
    tags=[TAG],
    summary="Excluir funcionário",
    description="Exclui (desativa) um funcionário do sistema.",
    responses={
        204: {"description": "Funcionário excluído com sucesso"},
        403: {"description": "Apenas administradores podem excluir"},
        404: {"description": "Funcionário não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
funcionario_view_schema = extend_schema_view(
    list=list_funcionarios,
    retrieve=retrieve_funcionario,
    create=create_funcionario,
    update=update_funcionario,
    partial_update=partial_update_funcionario,
    destroy=destroy_funcionario,
)

# Horário de Trabalho
list_horarios = extend_schema(
    tags=[TAG],
    summary="Listar horários de trabalho",
    description="Retorna a lista de horários de trabalho dos funcionários.",
    responses={200: envelop(HorarioTrabalhoSerializer(many=True), paginated=True)}
)

retrieve_horario = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um horário",
    description="Retorna os detalhes de um horário de trabalho específico.",
    responses={200: envelop(HorarioTrabalhoSerializer)}
)

create_horario = extend_schema(
    tags=[TAG],
    summary="Criar novo horário",
    description="Cria um novo horário de trabalho para um funcionário.",
    request=HorarioTrabalhoSerializer,
    responses={201: envelop(HorarioTrabalhoSerializer)}
)

update_horario = extend_schema(
    tags=[TAG],
    summary="Atualizar horário",
    description="Atualiza um horário de trabalho existente.",
    request=HorarioTrabalhoSerializer,
    responses={200: envelop(HorarioTrabalhoSerializer)}
)

partial_update_horario = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente um horário",
    description="Atualiza parcialmente um horário de trabalho.",
    request=HorarioTrabalhoSerializer,
    responses={200: envelop(HorarioTrabalhoSerializer)}
)

destroy_horario = extend_schema(
    tags=[TAG],
    summary="Excluir horário",
    description="Remove um horário de trabalho.",
    responses={204: {"description": "Horário excluído com sucesso"}}
)

horario_trabalho_view_schema = extend_schema_view(
    list=list_horarios,
    retrieve=retrieve_horario,
    create=create_horario,
    update=update_horario,
    partial_update=partial_update_horario,
    destroy=destroy_horario,
)

