# apps/agendamentos/admin.py
from django.contrib import admin
from .models import Agendamento


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'cliente', 'servico', 'data_hora', 'status', 'funcionario', 'ativo']
    list_filter = ['status', 'data_hora', 'ativo', 'data_criacao']
    search_fields = ['pet__nome', 'cliente__usuario__nome', 'servico__tipo']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_hora'

