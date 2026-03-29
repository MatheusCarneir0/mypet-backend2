# apps/pets/views.py
"""
Views para gerenciamento de pets.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Pet
from .serializers import (
    PetSerializer,
    PetListSerializer,
    PetCreateSerializer,
    PetUpdateSerializer,
    PetDetailSerializer
)
from apps.core.permissions import IsOwnerOrAdmin, IsFuncionario
from apps.swagger.pets import (
    list_pets, retrieve_pet, create_pet, update_pet,
    partial_update_pet, destroy_pet, historico_pet,
    choices_pet, upload_foto_pet
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
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
class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Pet.
    """
    queryset = Pet.objects.filter(ativo=True).select_related('cliente__usuario')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome', 'raca', 'cliente__usuario__nome']
    filterset_fields = ['cliente', 'especie']
    ordering_fields = ['nome', 'data_criacao']
    ordering = ['-data_criacao']
    
    def get_permissions(self):
        """
        Permissões:
        - list: Cliente vê apenas os seus (filtrado por get_queryset), Funcionário vê todos
        - retrieve: Autenticado (mas filtrado por get_queryset)
        - create: Cliente autenticado ou Funcionário/Admin
        - update/partial_update: Apenas o dono do pet ou Funcionário/Admin
        - destroy: Apenas o dono do pet ou Funcionário/Admin
        """
        if self.action == 'choices':
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]  # Apenas dono ou Funcionário/Admin
        return [IsAuthenticated()]  # list, retrieve, create
    
    def perform_create(self, serializer):
        """
        Força o cliente a ser o próprio usuário autenticado.
        Apenas funcionário/admin podem especificar outro cliente.
        """
        user = self.request.user
        if user.is_cliente:
            serializer.save(cliente=user.cliente)
        else:
            serializer.save()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PetListSerializer
        elif self.action == 'create':
            return PetCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PetUpdateSerializer
        elif self.action == 'retrieve':
            return PetDetailSerializer  # Inclui informações do 'Cuidador' (Dono)
        return PetSerializer
    
    def get_queryset(self):
        """
        Filtrar pets baseado no tipo de usuário.
        Filtro Automático obrigatório:
        - Se for Cliente, retornar apenas os pets dele
        - Se for Funcionário/Admin, retornar todos
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Cliente vê apenas seus pets
        if user.is_cliente:
            try:
                return queryset.filter(cliente__usuario=user)
            except:
                return queryset.none()
        
        # Funcionário e Administrador vêem todos
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """
        Implementar Soft Delete no destroy de Pets.
        """
        instance = self.get_object()
        instance.delete()  # Soft delete via BaseModel
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        """
        GET /pets/{id}/historico/
        Listar o HistoricoAtendimento vinculado a esse pet (UC09).
        """
        pet = self.get_object()
        
        # Verificar permissão: cliente só vê histórico de seus pets
        if request.user.is_cliente:
            if pet.cliente.usuario != request.user:
                return Response({
                    'error': 'Você não tem permissão para ver o histórico deste pet.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        historico = pet.historico_atendimentos.all().order_by('-data_atendimento')
        
        from apps.historico.serializers import HistoricoAtendimentoListSerializer
        serializer = HistoricoAtendimentoListSerializer(historico, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Override authentication_classes for the choices action
    # (action-level permission_classes=[AllowAny] alone isn't sufficient
    # because JWT auth raises 401 before permissions are checked)
    @action(detail=False, methods=['get'], url_path='choices',
            permission_classes=[AllowAny], authentication_classes=[])
    def choices(self, request):
        """
        GET /pets/choices/
        Retorna as opções válidas de espécie e porte para uso no frontend.
        AllowAny: são dados estáticos de configuração.
        """
        return Response({
            'especies': [
                {'value': k, 'label': v}
                for k, v in Pet.Especie.choices
            ],
            'portes': [
                {'value': k, 'label': v}
                for k, v in Pet.Porte.choices
            ],
        }, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        url_path='foto',
        permission_classes=[IsOwnerOrAdmin],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_foto(self, request, pk=None):
        """
        POST /pets/{id}/foto/
        Faz upload de foto do pet. Apenas o dono ou admin pode alterar.
        Aceita multipart/form-data com campo 'foto'.
        """
        pet = self.get_object()
        foto = request.FILES.get('foto')

        if not foto:
            return Response(
                {'error': 'Nenhuma foto foi enviada. Use o campo "foto".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar tipo
        TIPOS_PERMITIDOS = ['image/jpeg', 'image/png']
        if foto.content_type not in TIPOS_PERMITIDOS:
            return Response(
                {'error': 'Formato inválido. Use JPG ou PNG.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar tamanho (5MB)
        if foto.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Foto muito grande. Máximo 5MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pet.foto = foto
        pet.save()

        foto_url = request.build_absolute_uri(pet.foto.url) if pet.foto else None
        return Response(
            {'message': 'Foto do pet atualizada com sucesso.', 'foto_url': foto_url},
            status=status.HTTP_200_OK,
        )
