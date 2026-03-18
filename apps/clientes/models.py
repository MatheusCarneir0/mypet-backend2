# apps/clientes/models.py
"""
Modelo de Cliente.
Estende Usuario com informações específicas de clientes.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.authentication.models import Usuario
from apps.core.models import BaseModel


class Cliente(BaseModel):
    """
    Modelo de Cliente da FarmaVet.
    Relacionamento 1:1 com Usuario.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='cliente',
        verbose_name=_('Usuário')
    )
    cpf = models.CharField(
        _('CPF'),
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato: 000.000.000-00'
            )
        ]
    )
    endereco = models.CharField(_('Endereço'), max_length=255)
    ponto_referencia = models.CharField(
        _('Ponto de Referência'),
        max_length=255,
        blank=True,
        default=''
    )
    cidade = models.CharField(_('Cidade'), max_length=100)
    estado = models.CharField(
        _('Estado'),
        max_length=2,
        choices=[
            ('CE', 'Ceará'),
            ('PI', 'Piauí'),
            ('RN', 'Rio Grande do Norte'),
        ],
        default='CE'
    )
    cep = models.CharField(
        _('CEP'),
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='CEP deve estar no formato: 00000-000'
            )
        ]
    )
    
    class Meta:
        db_table = 'clientes'
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['usuario__nome']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['cidade', 'estado']),
        ]
    
    def __str__(self):
        return f'{self.usuario.nome} - {self.cpf}'
    
    @property
    def total_pets(self):
        """Retorna o número total de pets do cliente."""
        return self.pets.filter(ativo=True).count()
    
    @property
    def total_agendamentos(self):
        """Retorna o número total de agendamentos do cliente."""
        return self.agendamentos.count()

