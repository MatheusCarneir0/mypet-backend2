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
from .services import ClienteService
from apps.core.permissions import IsAdminOrSuperUser, IsOwnerOrAdmin
from apps.swagger.clientes import cliente_view_schema


@cliente_view_schema
class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Cliente.
    """
    queryset = Cliente.objects.filter(ativo=True).select_related('usuario')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['usuario__nome', 'usuario__email', 'cpf', 'cidade']
    ordering_fields = ['usuario__nome', 'data_criacao']
    ordering = ['-data_criacao']
    
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
            from apps.core.permissions import IsFuncionario
            return [IsFuncionario()]  # Apenas Funcionário/Admin pode listar todos (RF12)
        elif self.action == 'create':
            return [AllowAny()]  # Público - qualquer um pode se cadastrar
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
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Retorna dados do cliente autenticado.
        """
        try:
            cliente = ClienteService.obter_cliente_por_usuario(request.user)
            serializer = ClienteDetailSerializer(cliente)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
