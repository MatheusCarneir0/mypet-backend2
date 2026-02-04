# apps/historico/models.py
"""
Modelo de Histórico de Atendimento.
Registro completo de todos os atendimentos realizados.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.pets.models import Pet
from apps.agendamentos.models import Agendamento
from apps.pagamentos.models import FormaPagamento
from apps.core.models import TimeStampedModel


class HistoricoAtendimento(TimeStampedModel):
    """
    Histórico completo de atendimento.
    Criado automaticamente quando um agendamento é concluído.
    """
    agendamento = models.OneToOneField(
        Agendamento,
        on_delete=models.PROTECT,
        related_name='historico',
        verbose_name=_('Agendamento')
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name='historico_atendimentos',
        verbose_name=_('Pet')
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='historicos',
        verbose_name=_('Forma de Pagamento')
    )
    data_atendimento = models.DateTimeField(
        _('Data do Atendimento')
    )
    tipo_servico = models.CharField(
        _('Tipo de Serviço'),
        max_length=100
    )
    observacoes = models.TextField(
        _('Observações'),
        blank=True,
        help_text='Observações sobre o atendimento realizado'
    )
    valor_pago = models.DecimalField(
        _('Valor Pago'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        db_table = 'historico_atendimentos'
        verbose_name = _('Histórico de Atendimento')
        verbose_name_plural = _('Históricos de Atendimento')
        ordering = ['-data_atendimento']
        indexes = [
            models.Index(fields=['pet', 'data_atendimento']),
            models.Index(fields=['data_atendimento']),
        ]
    
    def __str__(self):
        return f'{self.pet.nome} - {self.tipo_servico} - {self.data_atendimento.strftime("%d/%m/%Y")}'

