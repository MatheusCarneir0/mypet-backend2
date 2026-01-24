"""
Configuração do Django Admin para o modelo User customizado.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin customizado para o modelo User.
    """
    
    # Campos exibidos na listagem
    list_display = [
        'username',
        'email',
        'get_full_name',
        'tipo_usuario',
        'ativo',
        'is_staff',
        'date_joined'  # CORRETO: usar date_joined
    ]
    
    list_filter = [
        'tipo_usuario',
        'ativo',
        'is_staff',
        'is_superuser',
        'date_joined'
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'telefone'
    ]
    
    ordering = ['-date_joined']  # CORRETO
    
    # Fieldsets para o formulário de edição
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name', 'email', 'telefone')
        }),
        (_('Tipo de Acesso'), {
            'fields': ('tipo_usuario', 'ativo')
        }),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets para criação de novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'tipo_usuario',
                'telefone'
            ),
        }),
    )
    
    def get_full_name(self, obj):
        """Retorna nome completo do usuário"""
        return obj.get_full_name() or '-'
    get_full_name.short_description = _('Nome Completo')