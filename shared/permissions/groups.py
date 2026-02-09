# shared/permissions/groups.py
"""
Permissões customizadas baseadas em Django Groups.
Sistema de autorização profissional seguindo boas práticas Django.
"""
from rest_framework import permissions


class IsCliente(permissions.BasePermission):
    """
    Permite acesso apenas para usuários do grupo CLIENTE.
    """
    message = "Você precisa ser um cliente para acessar este recurso."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='CLIENTE').exists()


class IsFuncionario(permissions.BasePermission):
    """
    Permite acesso apenas para usuários do grupo FUNCIONARIO.
    """
    message = "Você precisa ser um funcionário para acessar este recurso."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='FUNCIONARIO').exists()


class IsAdministrador(permissions.BasePermission):
    """
    Permite acesso apenas para usuários do grupo ADMINISTRADOR.
    """
    message = "Você precisa ser um administrador para acessar este recurso."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='ADMINISTRADOR').exists()


class IsFuncionarioOrAdmin(permissions.BasePermission):
    """
    Permite acesso para FUNCIONARIO ou ADMINISTRADOR.
    Útil para endpoints de gestão que não precisam ser exclusivos do admin.
    """
    message = "Você precisa ser um funcionário ou administrador para acessar este recurso."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name__in=['FUNCIONARIO', 'ADMINISTRADOR']).exists()


class IsClienteOwner(permissions.BasePermission):
    """
    Permite que cliente acesse apenas seus próprios recursos.
    Funcionários e admins têm acesso a todos.
    """
    message = "Você só pode acessar seus próprios recursos."
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin e Funcionário têm acesso total
        if user.groups.filter(name__in=['FUNCIONARIO', 'ADMINISTRADOR']).exists():
            return True
        
        # Cliente só acessa seus próprios recursos
        if user.groups.filter(name='CLIENTE').exists():
            # Verifica se o objeto tem relação com o usuário
            if hasattr(obj, 'usuario'):
                return obj.usuario == user
            elif hasattr(obj, 'cliente') and hasattr(obj.cliente, 'usuario'):
                return obj.cliente.usuario == user
        
        return False


class ReadOnlyForCliente(permissions.BasePermission):
    """
    Cliente: apenas leitura (GET, HEAD, OPTIONS)
    Funcionário/Admin: acesso completo
    """
    message = "Clientes têm acesso somente leitura a este recurso."
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Admin e Funcionário têm acesso total
        if user.groups.filter(name__in=['FUNCIONARIO', 'ADMINISTRADOR']).exists():
            return True
        
        # Cliente apenas métodos seguros (GET, HEAD, OPTIONS)
        if user.groups.filter(name='CLIENTE').exists():
            return request.method in permissions.SAFE_METHODS
        
        return False
