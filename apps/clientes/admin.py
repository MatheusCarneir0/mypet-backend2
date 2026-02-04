# apps/clientes/admin.py
from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cpf', 'cidade', 'estado', 'ativo', 'data_criacao']
    list_filter = ['estado', 'cidade', 'ativo', 'data_criacao']
    search_fields = ['usuario__nome', 'usuario__email', 'cpf', 'cidade']
    readonly_fields = ['data_criacao', 'data_atualizacao']

