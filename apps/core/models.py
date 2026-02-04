# apps/core/models.py
"""
Modelos abstratos base para reutilização em toda a aplicação.
Princípio DRY (Don't Repeat Yourself) e SOLID.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstrato que adiciona campos de timestamp.
    Utilizado em praticamente todos os modelos para auditoria.
    """
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True,
        help_text='Data e hora de criação do registro'
    )
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True,
        help_text='Data e hora da última atualização'
    )
    
    class Meta:
        abstract = True
        ordering = ['-data_criacao']


class SoftDeleteModel(models.Model):
    """
    Modelo abstrato que implementa soft delete.
    Registros não são deletados fisicamente, apenas marcados como inativos.
    Importante para LGPD e auditoria.
    """
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se o registro está ativo'
    )
    data_exclusao = models.DateTimeField(
        'Data de Exclusão',
        null=True,
        blank=True,
        help_text='Data e hora da exclusão lógica'
    )
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Sobrescreve o método delete para fazer soft delete.
        """
        self.ativo = False
        self.data_exclusao = timezone.now()
        self.save()
    
    def hard_delete(self):
        """
        Método para deletar fisicamente quando necessário.
        """
        super().delete()


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamp e soft delete.
    Utilizado como base para a maioria dos modelos.
    """
    class Meta:
        abstract = True

