# apps/pets/models.py
"""
Modelo de Pet.
Representa os animais de estimação cadastrados no sistema.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.clientes.models import Cliente
from apps.core.models import BaseModel


class Pet(BaseModel):
    """
    Modelo de Pet (animal de estimação).
    Cada pet pertence a um cliente.
    """
    class Especie(models.TextChoices):
        CAO = 'CAO', _('Cão')
        GATO = 'GATO', _('Gato')
        PASSARO = 'PASSARO', _('Pássaro')
        COELHO = 'COELHO', _('Coelho')
        OUTROS = 'OUTROS', _('Outros')
    
    class Porte(models.TextChoices):
        MINI = 'MINI', _('Mini (até 5kg)')
        PEQUENO = 'PEQUENO', _('Pequeno (5-10kg)')
        MEDIO = 'MEDIO', _('Médio (10-20kg)')
        GRANDE = 'GRANDE', _('Grande (20-40kg)')
        GIGANTE = 'GIGANTE', _('Gigante (acima de 40kg)')
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pets',
        verbose_name=_('Cliente')
    )
    nome = models.CharField(_('Nome'), max_length=100)
    especie = models.CharField(
        _('Espécie'),
        max_length=10,
        choices=Especie.choices
    )
    raca = models.CharField(_('Raça'), max_length=100)
    idade = models.PositiveIntegerField(
        _('Idade'),
        help_text='Idade em anos',
        null=True,
        blank=True
    )
    data_nascimento = models.DateField(
        _('Data de Nascimento'),
        null=True,
        blank=True,
        help_text='Data de nascimento do pet'
    )
    peso = models.DecimalField(
        _('Peso'),
        max_digits=5,
        decimal_places=2,
        help_text='Peso em quilogramas'
    )
    porte = models.CharField(
        _('Porte'),
        max_length=10,
        choices=Porte.choices,
        blank=True
    )
    foto = models.ImageField(
        _('Foto'),
        upload_to='pets/fotos/',
        blank=True,
        null=True
    )
    observacoes = models.TextField(
        _('Observações'),
        blank=True,
        help_text='Alergias, medicações, comportamento, etc.'
    )
    
    class Meta:
        db_table = 'pets'
        verbose_name = _('Pet')
        verbose_name_plural = _('Pets')
        ordering = ['cliente', 'nome']
        indexes = [
            models.Index(fields=['cliente', 'ativo']),
            models.Index(fields=['especie']),
        ]
    
    def __str__(self):
        return f'{self.nome} ({self.especie}) - {self.cliente.usuario.nome}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve save para calcular porte automaticamente.
        """
        if self.peso:
            if self.peso < 5:
                self.porte = self.Porte.MINI
            elif self.peso < 10:
                self.porte = self.Porte.PEQUENO
            elif self.peso < 20:
                self.porte = self.Porte.MEDIO
            elif self.peso < 40:
                self.porte = self.Porte.GRANDE
            else:
                self.porte = self.Porte.GIGANTE
        
        super().save(*args, **kwargs)
    
    @property
    def total_atendimentos(self):
        """Retorna o número total de atendimentos do pet."""
        return self.historico_atendimentos.count()

