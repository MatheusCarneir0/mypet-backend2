# apps/pagamentos/admin.py
from django.contrib import admin
from .models import FormaPagamento, TransacaoPagamento


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo', 'data_criacao']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']


@admin.register(TransacaoPagamento)
class TransacaoPagamentoAdmin(admin.ModelAdmin):
    list_display = ['agendamento', 'forma_pagamento', 'valor', 'status', 'data_pagamento', 'data_criacao']
    list_filter = ['status', 'forma_pagamento', 'data_pagamento', 'data_criacao']
    search_fields = ['agendamento__pet__nome', 'numero_transacao', 'pix_txid']
    readonly_fields = ['data_criacao', 'data_atualizacao']

