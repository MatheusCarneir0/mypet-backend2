"""
Selectors do app users (queries otimizadas).

Selectors são responsáveis por encapsular queries complexas e otimizadas,
seguindo o padrão Repository/Selector para separação de responsabilidades.
"""
from typing import List, Optional
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q, Count, Prefetch

User = get_user_model()


class UserSelector:
    """
    Selector para queries relacionadas a usuários.
    
    Centraliza queries otimizadas com select_related, prefetch_related
    e outras otimizações de performance.
    """
    
    @staticmethod
    def get_active_users() -> QuerySet[User]:
        """
        Retorna todos os usuários ativos.
        
        Returns:
            QuerySet de usuários ativos ordenados por data de cadastro
        """
        return User.objects.get_active().order_by('-data_cadastro')
    
    @staticmethod
    def get_users_by_type(tipo_usuario: str, active_only: bool = True) -> QuerySet[User]:
        """
        Retorna usuários filtrados por tipo.
        
        Args:
            tipo_usuario: Tipo de usuário (CLIENTE, FUNCIONARIO, ADMIN)
            active_only: Se True, retorna apenas usuários ativos
            
        Returns:
            QuerySet de usuários do tipo especificado
        """
        queryset = User.objects.filter(tipo_usuario=tipo_usuario)
        if active_only:
            queryset = queryset.filter(ativo=True)
        return queryset.order_by('-data_cadastro')
    
    @staticmethod
    def get_clients(active_only: bool = True) -> QuerySet[User]:
        """
        Retorna todos os clientes.
        
        Args:
            active_only: Se True, retorna apenas clientes ativos
            
        Returns:
            QuerySet de clientes
        """
        queryset = User.objects.get_clients()
        if not active_only:
            queryset = User.objects.filter(tipo_usuario=User.TipoUsuario.CLIENTE)
        return queryset.order_by('-data_cadastro')
    
    @staticmethod
    def get_funcionarios(active_only: bool = True) -> QuerySet[User]:
        """
        Retorna todos os funcionários.
        
        Args:
            active_only: Se True, retorna apenas funcionários ativos
            
        Returns:
            QuerySet de funcionários
        """
        queryset = User.objects.get_funcionarios()
        if not active_only:
            queryset = User.objects.filter(tipo_usuario=User.TipoUsuario.FUNCIONARIO)
        return queryset.order_by('-data_cadastro')
    
    @staticmethod
    def get_admins(active_only: bool = True) -> QuerySet[User]:
        """
        Retorna todos os administradores.
        
        Args:
            active_only: Se True, retorna apenas administradores ativos
            
        Returns:
            QuerySet de administradores
        """
        queryset = User.objects.get_admins()
        if not active_only:
            queryset = User.objects.filter(tipo_usuario=User.TipoUsuario.ADMIN)
        return queryset.order_by('-data_cadastro')
    
    @staticmethod
    def search_users(query: str, active_only: bool = True) -> QuerySet[User]:
        """
        Busca usuários por nome, email ou username.
        
        Args:
            query: Termo de busca
            active_only: Se True, retorna apenas usuários ativos
            
        Returns:
            QuerySet de usuários que correspondem à busca
        """
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
        if active_only:
            queryset = queryset.filter(ativo=True)
        
        return queryset.order_by('-data_cadastro')
    
    @staticmethod
    def get_users_with_stats() -> QuerySet[User]:
        """
        Retorna usuários com estatísticas agregadas.
        
        Returns:
            QuerySet de usuários com contagens relacionadas
        """
        return User.objects.get_active().annotate(
            # Aqui podem ser adicionadas anotações quando outros apps forem implementados
            # total_pets=Count('cliente__pets', distinct=True),
            # total_agendamentos=Count('cliente__agendamentos', distinct=True),
        )

