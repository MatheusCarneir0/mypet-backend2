# apps/agendamentos/models.py
"""
Modelo de Agendamento.
Representa os agendamentos de serviços realizados pelos clientes.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

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

    class StatusPagamento(models.TextChoices):
        PENDENTE = 'PENDENTE', _('Pendente')
        PAGO = 'PAGO', _('Pago')
        FALHOU = 'FALHOU', _('Falhou')
    
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
    duracao_real = models.PositiveIntegerField(
        _('Duração Real (min)'),
        null=True,
        blank=True,
        help_text='Duração efetiva considerando o porte do pet. Calculada ao criar.'
    )
    status_pagamento = models.CharField(
        _('Status do Pagamento'),
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.PENDENTE
    )
    valor_pago = models.DecimalField(
        _('Valor Pago'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
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
        from apps.agendamentos.validators import AgendamentoValidator
        
        valido_pet, err_pet = AgendamentoValidator.validar_pet_pertence_cliente(self.pet, self.cliente)
        if not valido_pet:
            raise ValidationError({'pet': _(err_pet)})
        
        # As demais validações complexas (tempo futuro, conflito na agenda, expediente)
        # agora residem na camada de Services via Validators para manter as regras de négocio em um só lugar
        # e evitar loops infinitos ao salvar em lotes e conflitos isolados.
        pass
        
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
        return self.status in [self.Status.EM_ANDAMENTO, self.Status.AGENDADO, self.Status.CONFIRMADO]
        
    @property
    def data_hora_fim(self):
        """Retorna o horário previsto para o término do serviço."""
        if self.data_hora and self.servico:
            duracao = self.duracao_real or self.servico.duracao_minutos
            return self.data_hora + timedelta(minutes=duracao)
        return self.data_hora

