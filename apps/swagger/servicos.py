# apps/swagger/servicos.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.servicos.serializers import (
    ServicoSerializer,
    ServicoListSerializer,
    ServicoCreateUpdateSerializer
)

TAG = "Agendamentos"  # Serviços estão relacionados a agendamentos

# Listagem
list_servicos = extend_schema(
    tags=[TAG],
    summary="Listar tipos de serviços",
    description="Retorna a lista de serviços disponíveis com tipos, preços e durações (Frame 434).",
    responses={200: envelop(ServicoListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_servico = extend_schema(
    tags=[TAG],
    summary="Obter detalhes de um serviço",
    description="Retorna os detalhes completos de um serviço específico.",
    responses={
        200: envelop(ServicoSerializer),
        404: {"description": "Serviço não encontrado"}
    }
)

# Criação
create_servico = extend_schema(
    tags=[TAG],
    summary="Criar novo serviço",
    description="Cria um novo serviço no sistema.",
    request=ServicoCreateUpdateSerializer,
    responses={
        201: envelop(ServicoSerializer),
        400: {"description": "Dados inválidos"}
    }
)

# Atualização
update_servico = extend_schema(
    tags=[TAG],
    summary="Atualizar serviço",
    description="Atualiza os dados de um serviço existente.",
    request=ServicoCreateUpdateSerializer,
    responses={
        200: envelop(ServicoSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Serviço não encontrado"}
    }
)

partial_update_servico = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente um serviço",
    description="Atualiza parcialmente os dados de um serviço existente.",
    request=ServicoCreateUpdateSerializer,
    responses={
        200: envelop(ServicoSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Serviço não encontrado"}
    }
)

# Exclusão
destroy_servico = extend_schema(
    tags=[TAG],
    summary="Excluir serviço",
    description="Exclui (desativa) um serviço do sistema.",
    responses={
        204: {"description": "Serviço excluído com sucesso"},
        404: {"description": "Serviço não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
servico_view_schema = extend_schema_view(
    list=list_servicos,
    retrieve=retrieve_servico,
    create=create_servico,
    update=update_servico,
    partial_update=partial_update_servico,
    destroy=destroy_servico,
)

