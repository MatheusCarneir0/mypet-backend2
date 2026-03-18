# apps/servicos/models.py
"""
Modelo de Serviço.
Representa os tipos de serviços oferecidos pela FarmaVet.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel


class Servico(BaseModel):
    """
    Modelo de Serviço oferecido pela FarmaVet.
    """
    class TipoServico(models.TextChoices):
        BANHO = 'BANHO', _('Banho')
        TOSA = 'TOSA', _('Tosa')
        BANHO_TOSA = 'BANHO_TOSA', _('Banho e Tosa')
        CORTE_UNHAS = 'CORTE_UNHAS', _('Corte de Unhas')
        BANHO_TERAPEUTICO = 'BANHO_TERAPEUTICO', _('Banho Terapêutico')
        VETERINARIO = 'VETERINARIO', _('Atendimento Veterinário')
        VACINA = 'VACINA', _('Vacinação')
        CONSULTA = 'CONSULTA', _('Consulta')
        EMERGENCIA = 'EMERGENCIA', _('Emergência')
    
    tipo = models.CharField(
        _('Tipo de Serviço'),
        max_length=20,
        choices=TipoServico.choices
    )
    descricao = models.TextField(_('Descrição'))
    preco = models.DecimalField(
        _('Preço'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duracao_minutos = models.PositiveIntegerField(
        _('Duração em Minutos'),
        help_text='Duração padrão do serviço (porte pequeno)'
    )
    duracao_medio_grande = models.PositiveIntegerField(
        _('Duração Médio/Grande (min)'),
        null=True,
        blank=True,
        help_text='Duração para porte médio/grande. Se vazio, usa a padrão.'
    )
    
    class Meta:
        db_table = 'servicos'
        verbose_name = _('Serviço')
        verbose_name_plural = _('Serviços')
        ordering = ['tipo']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - R$ {self.preco}'

