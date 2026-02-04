# apps/relatorios/admin.py
from django.contrib import admin
from .models import Relatorio


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'formato', 'administrador', 'data_geracao', 'arquivo']
    list_filter = ['tipo', 'formato', 'data_geracao']
    search_fields = ['administrador__nome', 'tipo']
    readonly_fields = ['data_geracao', 'data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_geracao'

