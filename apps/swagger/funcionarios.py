# apps/swagger/funcionarios.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.funcionarios.serializers import (
    FuncionarioSerializer,
    FuncionarioListSerializer,
    FuncionarioCreateSerializer,
    FuncionarioUpdateSerializer
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

