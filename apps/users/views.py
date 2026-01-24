"""
Views do app users.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from apps.users.services import UserService
from apps.users.selectors import UserSelector
from core.permissions import IsAdminUser, IsOwnerOrAdmin
from core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)
User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="Listar usuários",
        description="Retorna uma lista paginada de usuários ativos."
    ),
    retrieve=extend_schema(
        summary="Detalhar usuário",
        description="Retorna os detalhes de um usuário específico."
    ),
    create=extend_schema(
        summary="Criar usuário",
        description="Cria um novo usuário no sistema."
    ),
    update=extend_schema(
        summary="Atualizar usuário",
        description="Atualiza todos os campos de um usuário."
    ),
    partial_update=extend_schema(
        summary="Atualizar usuário parcialmente",
        description="Atualiza campos específicos de um usuário."
    ),
    destroy=extend_schema(
        summary="Deletar usuário",
        description="Remove um usuário do sistema (soft delete)."
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários.
    
    Endpoints disponíveis:
    - GET /api/v1/users/ - Lista usuários
    - POST /api/v1/users/ - Cria usuário
    - GET /api/v1/users/{id}/ - Detalha usuário
    - PUT/PATCH /api/v1/users/{id}/ - Atualiza usuário
    - DELETE /api/v1/users/{id}/ - Remove usuário
    - POST /api/v1/users/{id}/activate/ - Ativa usuário (admin only)
    - POST /api/v1/users/{id}/deactivate/ - Desativa usuário (admin only)
    - GET /api/v1/users/me/ - Retorna usuário autenticado
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Retorna queryset filtrado e otimizado.
        
        Filtros disponíveis:
        - tipo_usuario: Filtra por tipo (CLIENTE, FUNCIONARIO, ADMIN)
        - search: Busca por nome, email ou username
        - active: Filtra por status ativo (true/false)
        """
        queryset = UserSelector.get_active_users()
        
        # Filtrar por tipo de usuário
        tipo_usuario = self.request.query_params.get('tipo_usuario')
        if tipo_usuario:
            queryset = queryset.filter(tipo_usuario=tipo_usuario)
        
        # Busca por texto
        search = self.request.query_params.get('search')
        if search:
            queryset = UserSelector.search_users(search)
        
        # Filtrar por status ativo
        active = self.request.query_params.get('active')
        if active is not None:
            active_bool = active.lower() == 'true'
            queryset = queryset.filter(ativo=active_bool) if not active_bool else queryset
        
        return queryset
    
    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view requer.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]  # Permitir registro público
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action in ['activate', 'deactivate']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado para a ação."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Cria um novo usuário.
        
        Permite registro público, mas valida todos os dados.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"Novo usuário criado: {user.username} ({user.tipo_usuario})")
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Atualiza um usuário."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Usuário atualizado: {instance.username} (ID: {instance.id})")
        
        return Response(serializer.data)
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Remove um usuário (soft delete).
        
        Ao invés de deletar fisicamente, desativa o usuário.
        """
        instance = self.get_object()
        
        # Soft delete: desativar ao invés de deletar
        if instance.ativo:
            UserService.deactivate_user(str(instance.id))
            logger.info(f"Usuário desativado via DELETE: {instance.username}")
        else:
            logger.warning(f"Tentativa de deletar usuário já inativo: {instance.username}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="Desativar usuário",
        description="Desativa um usuário no sistema. Apenas administradores podem executar esta ação."
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, id=None):
        """Desativa um usuário."""
        try:
            user = UserService.deactivate_user(id)
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Ativar usuário",
        description="Ativa um usuário no sistema. Apenas administradores podem executar esta ação."
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, id=None):
        """Ativa um usuário."""
        user = UserService.activate_user(id)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Meu perfil",
        description="Retorna informações do usuário autenticado."
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna informações do usuário autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Verificar disponibilidade de email",
        description="Verifica se um email está disponível para uso."
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def check_email(self, request):
        """
        Verifica se um email está disponível.
        
        Query params:
        - email: Email a verificar
        """
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Parâmetro email é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = UserService.check_email_exists(email)
        return Response({
            'email': email,
            'available': not exists
        })
    
    @extend_schema(
        summary="Verificar disponibilidade de username",
        description="Verifica se um username está disponível para uso."
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def check_username(self, request):
        """
        Verifica se um username está disponível.
        
        Query params:
        - username: Username a verificar
        """
        username = request.query_params.get('username')
        if not username:
            return Response(
                {'error': 'Parâmetro username é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = UserService.check_username_exists(username)
        return Response({
            'username': username,
            'available': not exists
        })

