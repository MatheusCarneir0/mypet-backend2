# apps/agendamentos/models.py
"""
Modelo de Agendamento.
Representa os agendamentos de serviços realizados pelos clientes.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.clientes.models import Cliente
from apps.pets.models import Pet
from apps.servicos.models import Servico
from apps.funcionarios.models import Funcionario
from apps.pagamentos.models import FormaPagamento
from apps.core.models import BaseModel


class Agendamento(BaseModel):
    """
    Modelo de Agendamento de serviço.
    """
    class Status(models.TextChoices):
        AGENDADO = 'AGENDADO', _('Agendado')
        CONFIRMADO = 'CONFIRMADO', _('Confirmado')
        EM_ANDAMENTO = 'EM_ANDAMENTO', _('Em Andamento')
        CONCLUIDO = 'CONCLUIDO', _('Concluído')
        CANCELADO = 'CANCELADO', _('Cancelado')
        NAO_COMPARECEU = 'NAO_COMPARECEU', _('Não Compareceu')
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='agendamentos',
        verbose_name=_('Cliente')
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name='agendamentos',
        verbose_name=_('Pet')
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name='agendamentos',
        verbose_name=_('Serviço')
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agendamentos',
        verbose_name=_('Funcionário Responsável')
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        related_name='agendamentos',
        verbose_name=_('Forma de Pagamento'),
        help_text='Forma de pagamento escolhida no momento do agendamento'
    )
    data_hora = models.DateTimeField(
        _('Data e Hora'),
        help_text='Data e hora do agendamento'
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADO
    )
    observacoes = models.TextField(
        _('Observações'),
        blank=True,
        help_text='Observações sobre o agendamento'
    )
    
    class Meta:
        db_table = 'agendamentos'
        verbose_name = _('Agendamento')
        verbose_name_plural = _('Agendamentos')
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['data_hora', 'status']),
            models.Index(fields=['cliente', 'data_hora']),
            models.Index(fields=['pet', 'data_hora']),
            models.Index(fields=['funcionario', 'data_hora']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['data_hora', 'funcionario'],
                condition=models.Q(status__in=['AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO']),
                name='unique_funcionario_horario'
            )
        ]
    
    def __str__(self):
        return f'{self.pet.nome} - {self.servico.tipo} - {self.data_hora.strftime("%d/%m/%Y %H:%M")}'
    
    def clean(self):
        """
        Validações customizadas do modelo.
        """
        # Validar que o pet pertence ao cliente
        if self.pet and self.cliente and self.pet.cliente != self.cliente:
            raise ValidationError({
                'pet': _('O pet selecionado não pertence a este cliente.')
            })
        
        # Validar que a data/hora é futura
        if self.data_hora and self.data_hora < timezone.now():
            raise ValidationError({
                'data_hora': _('Não é possível agendar para uma data/hora no passado.')
            })
        
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def pode_cancelar(self):
        """Verifica se o agendamento pode ser cancelado."""
        return self.status in [self.Status.AGENDADO, self.Status.CONFIRMADO]
    
    @property
    def pode_iniciar(self):
        """Verifica se o agendamento pode ser iniciado."""
        return self.status in [self.Status.AGENDADO, self.Status.CONFIRMADO]
    
    @property
    def pode_concluir(self):
        """Verifica se o agendamento pode ser concluído."""
        return self.status == self.Status.EM_ANDAMENTO

