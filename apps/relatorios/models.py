# apps/relatorios/models.py
"""
Modelo de Relatório.
Gerencia os relatórios gerenciais do sistema.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Usuario
from apps.authentication.constants import UserGroups
from apps.core.models import TimeStampedModel


class Relatorio(TimeStampedModel):
    """
    Modelo de Relatório Gerencial.
    """
    class TipoRelatorio(models.TextChoices):
        SERVICOS = 'SERVICOS', _('Relatório de Serviços')
        FATURAMENTO = 'FATURAMENTO', _('Relatório de Faturamento')
        CLIENTES = 'CLIENTES', _('Relatório de Clientes')
        FUNCIONARIOS = 'FUNCIONARIOS', _('Relatório de Funcionários')
        AGENDAMENTOS = 'AGENDAMENTOS', _('Relatório de Agendamentos')
    
    class FormatoRelatorio(models.TextChoices):
        PDF = 'PDF', _('PDF')
        EXCEL = 'EXCEL', _('Excel')
        CSV = 'CSV', _('CSV')
    
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='relatorios',
        verbose_name=_('Administrador'),
        limit_choices_to={'groups__name': UserGroups.ADMINISTRADOR}
    )
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoRelatorio.choices
    )
    formato = models.CharField(
        _('Formato'),
        max_length=10,
        choices=FormatoRelatorio.choices,
        default=FormatoRelatorio.PDF
    )
    data_geracao = models.DateTimeField(
        _('Data de Geração'),
        auto_now_add=True
    )
    filtros = models.JSONField(
        _('Filtros'),
        help_text='Filtros aplicados ao relatório em formato JSON',
        default=dict
    )
    arquivo = models.FileField(
        _('Arquivo'),
        upload_to='relatorios/%Y/%m/',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'relatorios'
        verbose_name = _('Relatório')
        verbose_name_plural = _('Relatórios')
        ordering = ['-data_geracao']
        indexes = [
            models.Index(fields=['administrador', 'data_geracao']),
            models.Index(fields=['tipo', 'data_geracao']),
        ]
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.data_geracao.strftime("%d/%m/%Y %H:%M")}'

