# apps/authentication/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['email', 'nome', 'tipo_usuario', 'ativo', 'is_staff', 'data_criacao']
    list_filter = ['tipo_usuario', 'ativo', 'is_staff', 'data_criacao']
    search_fields = ['email', 'nome', 'telefone']
    ordering = ['-data_criacao']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Extras', {'fields': ('tipo_usuario', 'telefone', 'ativo')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Extras', {'fields': ('tipo_usuario', 'telefone')}),
    )

