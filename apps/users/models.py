import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Model User customizado seguindo o diagrama ER.
    Usa UUID como primary key para melhor segurança em APIs.
    """
    
    # Choices para tipo de usuário
    class TipoUsuario(models.TextChoices):
        CLIENTE = 'CLIENTE', _('Cliente')
        FUNCIONARIO = 'FUNCIONARIO', _('Funcionário')
        ADMIN = 'ADMIN', _('Administrador')
    
    # Primary Key como UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    # Sobrescrever email para torná-lo obrigatório e único
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("Já existe um usuário com este email."),
        }
    )
    
    # Campos adicionais do diagrama
    telefone = models.CharField(
        _('telefone'),
        max_length=15,
        blank=True,
        help_text='Formato: (85) 99999-9999'
    )
    
    tipo_usuario = models.CharField(
        _('tipo de usuário'),
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.CLIENTE,
        db_index=True  # Índice para queries rápidas
    )
    
    ativo = models.BooleanField(
        _('ativo'),
        default=True,
        help_text='Indica se o usuário pode fazer login'
    )
    
    # Campos de timestamp
    date_joined = models.DateTimeField(
        _('data de cadastro'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('atualizado em'),
        auto_now=True
    )
    
    # Configurações
    USERNAME_FIELD = 'email'  # Login por email
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']  # Mais recentes primeiro
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario']),
            models.Index(fields=['-date_joined']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    # Métodos helper para verificar tipo de usuário
    def is_cliente(self) -> bool:
        """Verifica se é cliente"""
        return self.tipo_usuario == self.TipoUsuario.CLIENTE
    
    def is_funcionario(self) -> bool:
        """Verifica se é funcionário"""
        return self.tipo_usuario == self.TipoUsuario.FUNCIONARIO
    
    def is_admin(self) -> bool:
        """Verifica se é administrador"""
        return self.tipo_usuario == self.TipoUsuario.ADMIN or self.is_superuser
    
    def get_full_name(self) -> str:
        """Retorna nome completo"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def save(self, *args, **kwargs):
        """
        Override save para garantir validações.
        Superusuários são sempre ADMIN.
        """
        if self.is_superuser:
            self.tipo_usuario = self.TipoUsuario.ADMIN
        
        super().save(*args, **kwargs)