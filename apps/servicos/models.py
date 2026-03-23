# apps/servicos/models.py
"""
Modelo de Serviço.
Representa os serviços oferecidos pela FarmaVet,
com os cargos profissionais que os executam.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel


class Servico(BaseModel):
    """
    Modelo de Serviço oferecido pela FarmaVet.
    O nome do serviço é livre e os profissionais que o realizam
    são indicados via relacionamento com ServicoCargo.
    """
    nome = models.CharField(
        _('Nome do Serviço'),
        max_length=100,
        help_text='Ex: Tosa Completa, Consulta Veterinária, Banho Terapêutico'
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
        help_text='Duração média estimada do serviço em minutos'
    )

    class Meta:
        db_table = 'servicos'
        verbose_name = _('Serviço')
        verbose_name_plural = _('Serviços')
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} - R$ {self.preco}'


class ServicoCargo(BaseModel):
    """
    Relacionamento entre um Serviço e os Cargos dos profissionais
    que estão aptos a realizá-lo.
    """
    # Importar choices do Funcionario evita duplicação
    CARGO_CHOICES = [
        ('ATENDENTE', _('Atendente')),
        ('TOSADOR', _('Tosador')),
        ('VETERINARIO', _('Veterinário')),
        ('GERENTE', _('Gerente')),
    ]

    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name='cargos',
        verbose_name=_('Serviço')
    )
    cargo = models.CharField(
        _('Cargo'),
        max_length=20,
        choices=CARGO_CHOICES
    )

    class Meta:
        db_table = 'servicos_cargos'
        verbose_name = _('Cargo do Serviço')
        verbose_name_plural = _('Cargos do Serviço')
        unique_together = ['servico', 'cargo']
        ordering = ['servico', 'cargo']

    def __str__(self):
        return f'{self.servico.nome} → {self.get_cargo_display()}'
