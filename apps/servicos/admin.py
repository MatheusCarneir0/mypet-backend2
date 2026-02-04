# apps/servicos/admin.py
from django.contrib import admin
from .models import Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'preco', 'duracao_minutos', 'ativo', 'data_criacao']
    list_filter = ['tipo', 'ativo', 'data_criacao']
    search_fields = ['tipo', 'descricao']
    readonly_fields = ['data_criacao', 'data_atualizacao']

