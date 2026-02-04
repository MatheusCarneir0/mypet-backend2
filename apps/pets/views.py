# apps/pets/views.py
"""
Views para gerenciamento de pets.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
from apps.swagger.pets import pet_view_schema


@pet_view_schema
class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Pet.
    """
    queryset = Pet.objects.filter(ativo=True).select_related('cliente__usuario')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome', 'raca', 'cliente__usuario__nome']
    ordering_fields = ['nome', 'data_criacao']
    ordering = ['-data_criacao']
    
    def get_permissions(self):
        """
        Permissões:
        - list: Cliente vê apenas os seus (filtrado por get_queryset), Funcionário vê todos
        - retrieve: Autenticado (mas filtrado por get_queryset)
        - create: Cliente autenticado
        - update/partial_update: Apenas o dono do pet ou Funcionário/Admin
        - destroy: Apenas o dono do pet ou Funcionário/Admin
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]  # Apenas dono ou Funcionário/Admin
        return [IsAuthenticated()]  # list, retrieve, create
    
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
