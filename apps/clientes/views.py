# apps/clientes/views.py
"""
Views para gerenciamento de clientes.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Cliente
from .serializers import (
    ClienteSerializer,
    ClienteListSerializer,
    ClienteCreateSerializer,
    ClienteUpdateSerializer,
    ClienteDetailSerializer
)
from apps.core.permissions import IsAdminOrSuperUser, IsOwnerOrAdmin, IsFuncionario
from apps.swagger.clientes import (
    list_clientes, retrieve_cliente, create_cliente,
    update_cliente, partial_update_cliente, destroy_cliente
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=list_clientes,
    retrieve=retrieve_cliente,
    create=create_cliente,
    update=update_cliente,
    partial_update=partial_update_cliente,
    destroy=destroy_cliente,
)
class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Cliente.
    IMPORTANTE: 
    - Cadastro via /auth/register/ (não POST /clientes/)
    - Atualização via /me/profile/ (não PUT/PATCH /clientes/{id}/)
    - Apenas GET e DELETE permitidos aqui (admin/funcionário)
    """
    queryset = Cliente.objects.filter(ativo=True).select_related('usuario')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['usuario__nome', 'usuario__email', 'cpf', 'cidade']
    ordering_fields = ['usuario__nome', 'data_criacao']
    ordering = ['-data_criacao']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        elif self.action == 'create':
            return ClienteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClienteUpdateSerializer
        elif self.action == 'retrieve':
            return ClienteDetailSerializer
        return ClienteSerializer
    
    def get_permissions(self):
        """
        Permissões:
        - list: Apenas Funcionário/Admin (RF12)
        - retrieve: Autenticado (mas filtrado por get_queryset)
        - create: Público (qualquer um pode se cadastrar)
        - update/partial_update: Apenas o dono ou Admin
        - destroy: Apenas Admin
        """
        if self.action == 'list':
            # IsFuncionario já inclui Administrador (ver permissions.py:28)
            from apps.core.permissions import IsFuncionario
            return [IsFuncionario()]
        elif self.action == 'create':
            from apps.core.permissions import IsFuncionario
            return [IsFuncionario()]  # Apenas funcionário/admin pode criar cliente
        elif self.action == 'destroy':
            from apps.core.permissions import IsAdministrador
            return [IsAdministrador()]  # Apenas Admin pode deletar
        elif self.action in ['update', 'partial_update']:
            return [IsOwnerOrAdmin()]  # Apenas o dono ou Admin pode atualizar
        return [IsAuthenticated()]  # retrieve e outras ações
    
    def get_queryset(self):
        """
        Filtrar clientes baseado no tipo de usuário.
        Cliente vê apenas seus próprios dados.
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Cliente vê apenas seus próprios dados
        if user.is_cliente:
            try:
                return queryset.filter(usuario=user)
            except:
                return queryset.none()
        
        # Funcionário e Administrador vêem todos
        return queryset
    

