# apps/funcionarios/models.py
"""
Modelo de Funcionário.
Estende Usuario com informações específicas de funcionários.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Usuario
from apps.core.models import BaseModel


class Funcionario(BaseModel):
    """
    Modelo de Funcionário da FarmaVet.
    Relacionamento 1:1 com Usuario.
    """
    class Cargo(models.TextChoices):
        ATENDENTE = 'ATENDENTE', _('Atendente')
        TOSADOR = 'TOSADOR', _('Tosador')
        VETERINARIO = 'VETERINARIO', _('Veterinário')
        GERENTE = 'GERENTE', _('Gerente')
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='funcionario',
        verbose_name=_('Usuário')
    )
    cargo = models.CharField(
        _('Cargo'),
        max_length=20,
        choices=Cargo.choices
    )
    horario_trabalho = models.CharField(
        _('Horário de Trabalho'),
        max_length=100,
        help_text='Ex: Segunda a Sexta, 08:00-17:00'
    )
    
    class Meta:
        db_table = 'funcionarios'
        verbose_name = _('Funcionário')
        verbose_name_plural = _('Funcionários')
        ordering = ['usuario__nome']
        indexes = [
            models.Index(fields=['cargo', 'ativo']),
        ]
    
    def __str__(self):
        return f'{self.usuario.nome} - {self.get_cargo_display()}'
    
    @property
    def total_atendimentos(self):
        """Retorna o número total de atendimentos realizados."""
        return self.agendamentos.filter(status='CONCLUIDO').count()

