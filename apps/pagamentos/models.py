# apps/pagamentos/models.py
"""
Modelos de Pagamento.
Sistema LOCAL sem gateway - cidade pequena.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
import uuid


class FormaPagamento(BaseModel):
    """
    Forma de pagamento aceita pela FarmaVet.
    """
    class TipoPagamento(models.TextChoices):
        DINHEIRO = 'DINHEIRO', _('Dinheiro')
        CARTAO_DEBITO = 'CARTAO_DEBITO', _('Cartão de Débito')
        CARTAO_CREDITO = 'CARTAO_CREDITO', _('Cartão de Crédito')
        PIX = 'PIX', _('PIX')
    
    nome = models.CharField(
        _('Nome'),
        max_length=50,
        unique=True
    )
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoPagamento.choices
    )
    descricao = models.TextField(
        _('Descrição'),
        blank=True
    )
    
    class Meta:
        db_table = 'formas_pagamento'
        verbose_name = _('Forma de Pagamento')
        verbose_name_plural = _('Formas de Pagamento')
        ordering = ['nome']
    
    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'


class TransacaoPagamento(BaseModel):
    """
    Registro de transação de pagamento LOCAL.
    Não usa gateway - sistema de cidade pequena.
    """
    class StatusPagamento(models.TextChoices):
        PENDENTE = 'PENDENTE', _('Pendente')
        CONFIRMADO = 'CONFIRMADO', _('Confirmado')
        CANCELADO = 'CANCELADO', _('Cancelado')
    
    agendamento = models.OneToOneField(
        'agendamentos.Agendamento',
        on_delete=models.PROTECT,
        related_name='pagamento',
        verbose_name=_('Agendamento')
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        related_name='transacoes',
        verbose_name=_('Forma de Pagamento')
    )
    valor = models.DecimalField(
        _('Valor'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.PENDENTE
    )
    
    # Campos específicos para DINHEIRO
    valor_recebido = models.DecimalField(
        _('Valor Recebido'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Valor em dinheiro recebido do cliente'
    )
    troco = models.DecimalField(
        _('Troco'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Valor do troco devolvido'
    )
    
    # Campos específicos para PIX
    pix_qrcode = models.ImageField(
        _('QR Code PIX'),
        upload_to='qrcodes/%Y/%m/',
        null=True,
        blank=True
    )
    pix_codigo = models.TextField(
        _('Código PIX Copia e Cola'),
        null=True,
        blank=True
    )
    pix_txid = models.CharField(
        _('Transaction ID'),
        max_length=100,
        null=True,
        blank=True
    )
    
    # Campos específicos para CARTÃO
    numero_transacao = models.CharField(
        _('Número da Transação'),
        max_length=100,
        null=True,
        blank=True,
        help_text='Número da transação na maquininha'
    )
    bandeira_cartao = models.CharField(
        _('Bandeira do Cartão'),
        max_length=50,
        null=True,
        blank=True,
        help_text='Ex: Visa, Mastercard, Elo'
    )
    ultimos_digitos = models.CharField(
        _('Últimos 4 Dígitos'),
        max_length=4,
        null=True,
        blank=True
    )
    
    data_pagamento = models.DateTimeField(
        _('Data do Pagamento'),
        null=True,
        blank=True
    )
    
    observacoes = models.TextField(
        _('Observações'),
        blank=True
    )
    
    class Meta:
        db_table = 'transacoes_pagamento'
        verbose_name = _('Transação de Pagamento')
        verbose_name_plural = _('Transações de Pagamento')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['agendamento']),
            models.Index(fields=['status', 'data_pagamento']),
        ]
    
    def __str__(self):
        return f'Pagamento #{self.id} - {self.forma_pagamento.nome} - R$ {self.valor}'
    
    def calcular_troco(self):
        """Calcula o troco para pagamentos em dinheiro."""
        if self.forma_pagamento.tipo == FormaPagamento.TipoPagamento.DINHEIRO:
            if self.valor_recebido:
                self.troco = self.valor_recebido - self.valor
        return self.troco

