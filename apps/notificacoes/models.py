# apps/notificacoes/models.py
"""
Modelo de Notificação.
Gerencia todas as notificações enviadas pelo sistema.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.agendamentos.models import Agendamento
from apps.core.models import TimeStampedModel


class Notificacao(TimeStampedModel):
    """
    Modelo de Notificação.
    Pode ser enviada por email ou SMS.
    """
    class TipoNotificacao(models.TextChoices):
        CONFIRMACAO = 'CONFIRMACAO', _('Confirmação de Agendamento')
        LEMBRETE = 'LEMBRETE', _('Lembrete de Agendamento')
        CANCELAMENTO = 'CANCELAMENTO', _('Cancelamento de Agendamento')
        CONCLUSAO = 'CONCLUSAO', _('Conclusão de Serviço')
        REAGENDAMENTO = 'REAGENDAMENTO', _('Reagendamento')
    
    class CanalNotificacao(models.TextChoices):
        EMAIL = 'EMAIL', _('E-mail')
        SMS = 'SMS', _('SMS')
        AMBOS = 'AMBOS', _('E-mail e SMS')
    
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name=_('Agendamento')
    )
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoNotificacao.choices
    )
    canal = models.CharField(
        _('Canal'),
        max_length=10,
        choices=CanalNotificacao.choices,
        default=CanalNotificacao.EMAIL
    )
    destinatario = models.CharField(
        _('Destinatário'),
        max_length=255,
        help_text='E-mail ou telefone do destinatário'
    )
    assunto = models.CharField(
        _('Assunto'),
        max_length=200
    )
    mensagem = models.TextField(
        _('Mensagem')
    )
    enviada = models.BooleanField(
        _('Enviada'),
        default=False
    )
    lida = models.BooleanField(
        _('Lida'),
        default=False,
        help_text='Indica se a notificação foi visualizada pelo usuário'
    )
    data_envio = models.DateTimeField(
        _('Data de Envio'),
        null=True,
        blank=True
    )
    tentativas = models.PositiveIntegerField(
        _('Tentativas'),
        default=0
    )
    erro = models.TextField(
        _('Erro'),
        blank=True,
        help_text='Mensagem de erro caso o envio falhe'
    )
    
    class Meta:
        db_table = 'notificacoes'
        verbose_name = _('Notificação')
        verbose_name_plural = _('Notificações')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['agendamento', 'tipo']),
            models.Index(fields=['enviada', 'data_criacao']),
        ]
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.destinatario} - {"Enviada" if self.enviada else "Pendente"}'

