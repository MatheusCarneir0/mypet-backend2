# apps/notificacoes/admin.py
from django.contrib import admin
from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['agendamento', 'tipo', 'canal', 'destinatario', 'enviada', 'data_envio', 'data_criacao']
    list_filter = ['tipo', 'canal', 'enviada', 'data_criacao']
    search_fields = ['destinatario', 'assunto', 'agendamento__pet__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']

