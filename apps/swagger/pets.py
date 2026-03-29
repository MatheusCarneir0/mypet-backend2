# apps/swagger/pets.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from apps.swagger.swagger_helper import envelop
from apps.pets.serializers import (
    PetDetailSerializer,
    PetListSerializer,
    PetCreateSerializer,
    PetUpdateSerializer
)
from apps.historico.serializers import HistoricoAtendimentoListSerializer

TAG = "Pets"

# Listagem
list_pets = extend_schema(
    tags=[TAG],
    summary="Listar meus pets",
    description="Retorna a lista de pets. Clientes veem automaticamente apenas seus próprios pets (Frame 434). Funcionários e administradores veem todos.",
    parameters=[
        OpenApiParameter(name='search', description='Buscar por nome, raça ou nome do cliente', required=False, type=str),
        OpenApiParameter(name='cliente', description='Filtrar por ID do cliente', required=False, type=int),
        OpenApiParameter(name='especie', description='Filtrar por espécie', required=False, type=str),
    ],
    responses={200: envelop(PetListSerializer(many=True), paginated=True)}
)

# Detalhes
retrieve_pet = extend_schema(
    tags=[TAG],
    summary="Detalhar pet",
    description="Retorna os detalhes completos de um pet com dados do cuidador (Dono) (Frame 435).",
    responses={
        200: envelop(PetDetailSerializer),
        404: {"description": "Pet não encontrado"}
    }
)

# Criação
create_pet = extend_schema(
    tags=[TAG],
    summary="Cadastrar pet",
    description="Cria um novo pet no sistema (Frame 433). Clientes podem criar pets para si mesmos.",
    request=PetCreateSerializer,
    responses={
        201: envelop(PetDetailSerializer),
        400: {"description": "Dados inválidos"}
    }
)

# Atualização
update_pet = extend_schema(
    tags=[TAG],
    summary="Editar pet",
    description="Atualiza os dados de um pet existente. Apenas o dono ou funcionário/admin pode editar.",
    request=PetUpdateSerializer,
    responses={
        200: envelop(PetDetailSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Pet não encontrado"}
    }
)

partial_update_pet = extend_schema(
    tags=[TAG],
    summary="Atualizar parcialmente um pet",
    description="Atualiza parcialmente os dados de um pet existente.",
    request=PetUpdateSerializer,
    responses={
        200: envelop(PetDetailSerializer),
        400: {"description": "Dados inválidos"},
        404: {"description": "Pet não encontrado"}
    }
)

# Exclusão
destroy_pet = extend_schema(
    tags=[TAG],
    summary="Excluir pet",
    description="Exclui (soft delete) um pet do sistema. Apenas o dono ou funcionário/admin pode excluir.",
    responses={
        204: {"description": "Pet excluído com sucesso"},
        404: {"description": "Pet não encontrado"}
    }
)

# Ações customizadas
historico_pet = extend_schema(
    tags=[TAG],
    summary="Histórico de serviços do pet",
    description="Retorna a lista de HistoricoAtendimento do pet específico.",
    responses={
        200: envelop(HistoricoAtendimentoListSerializer(many=True)),
        404: {"description": "Pet não encontrado"}
    }
)

choices_pet = extend_schema(
    tags=[TAG],
    summary="Opções de espécie e porte",
    description="Retorna as opções válidas de espécie e porte para uso em formulários.",
    responses={
        200: envelop({
            "type": "object",
            "properties": {
                "especies": {"type": "array", "items": {"type": "object"}},
                "portes": {"type": "array", "items": {"type": "object"}}
            }
        })
    }
)

upload_foto_pet = extend_schema(
    tags=[TAG],
    summary="Upload de foto do pet",
    description="Faz upload de foto do pet. Aceita multipart/form-data com campo 'foto'.",
    responses={
        200: envelop({"type": "object", "properties": {"message": {"type": "string"}, "foto_url": {"type": "string"}}}),
        400: {"description": "Dados inválidos"},
        404: {"description": "Pet não encontrado"}
    }
)

# Schema view para aplicar todos os decorators de uma vez
pet_view_schema = extend_schema_view(
    list=list_pets,
    retrieve=retrieve_pet,
    create=create_pet,
    update=update_pet,
    partial_update=partial_update_pet,
    destroy=destroy_pet,
    historico=historico_pet,
    choices=choices_pet,
    upload_foto=upload_foto_pet,
)

