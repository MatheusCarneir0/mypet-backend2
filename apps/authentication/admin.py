# apps/authentication/admin.py
"""
Configuração do Django Admin para o modelo Usuario.
Refatorado para usar Django Groups ao invés de tipo_usuario.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


def get_grupos(obj):
    """Retorna grupos do usuário como string."""
    return ", ".join(obj.get_grupos())
get_grupos.short_description = 'Grupos'


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Admin customizado para Usuario.
    Exibe grupos ao invés de tipo_usuario.
    """
    list_display = ['email', 'nome', get_grupos, 'ativo', 'is_staff', 'data_criacao']
    list_filter = ['groups', 'ativo', 'is_staff', 'data_criacao']
    search_fields = ['email', 'nome', 'telefone']
    ordering = ['-data_criacao']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'telefone', 'foto')}),
        ('Permissões', {'fields': ('ativo', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'data_criacao', 'data_atualizacao')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'telefone', 'password1', 'password2'),
        }),
        ('Permissões', {
            'fields': ('groups',),
        }),
    )
    
    readonly_fields = ['data_criacao', 'data_atualizacao']
    filter_horizontal = ('groups', 'user_permissions')
