# apps/historico/admin.py
from django.contrib import admin
from .models import HistoricoAtendimento


@admin.register(HistoricoAtendimento)
class HistoricoAtendimentoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'tipo_servico', 'data_atendimento', 'valor_pago', 'forma_pagamento', 'data_criacao']
    list_filter = ['tipo_servico', 'data_atendimento', 'forma_pagamento', 'data_criacao']
    search_fields = ['pet__nome', 'pet__cliente__usuario__nome', 'tipo_servico']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_atendimento'

