# apps/core/permissions.py
"""
Permissões customizadas para a aplicação.
"""
from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """
    Permissão para apenas administradores.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_administrador
        )


class IsFuncionario(BasePermission):
    """
    Permissão para funcionários e administradores.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_funcionario or request.user.is_administrador)
        )


class IsCliente(BasePermission):
    """
    Permissão para clientes.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_cliente
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permissão para dono do recurso ou administrador.
    """
    def has_object_permission(self, request, view, obj):
        # Administrador tem acesso total
        if request.user.is_administrador:
            return True
        
        # Verificar se é o dono
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        if hasattr(obj, 'cliente'):
            return obj.cliente.usuario == request.user
        
        return False


class IsAdminOrSuperUser(BasePermission):
    """
    Permissão para funcionários com cargo superior ou administradores.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_administrador:
            return True
        
        if request.user.is_funcionario:
            from apps.funcionarios.models import Funcionario
            return request.user.funcionario.cargo in [
                Funcionario.Cargo.GERENTE,
                Funcionario.Cargo.VETERINARIO
            ]
        
        return False

