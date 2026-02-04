# apps/authentication/models.py
"""
Modelo de usuário customizado.
Base para Cliente, Funcionario e Administrador.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class UsuarioManager(BaseUserManager):
    """
    Manager customizado para o modelo Usuario.
    """
    def create_user(self, email, senha=None, **extra_fields):
        """
        Cria e salva um usuário regular.
        """
        if not email:
            raise ValueError(_('O email é obrigatório'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(senha)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, senha=None, **extra_fields):
        """
        Cria e salva um superusuário.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tipo_usuario', Usuario.TipoUsuario.ADMINISTRADOR)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))
        
        return self.create_user(email, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Modelo de usuário customizado.
    Usa email como identificador único ao invés de username.
    """
    class TipoUsuario(models.TextChoices):
        CLIENTE = 'CLIENTE', _('Cliente')
        FUNCIONARIO = 'FUNCIONARIO', _('Funcionário')
        ADMINISTRADOR = 'ADMINISTRADOR', _('Administrador')
    
    email = models.EmailField(
        _('Email'),
        unique=True,
        error_messages={
            'unique': _('Já existe um usuário com este email.'),
        }
    )
    nome = models.CharField(_('Nome Completo'), max_length=150)
    telefone = models.CharField(
        _('Telefone'),
        max_length=15,
        help_text='Formato: (88) 99999-9999'
    )
    foto = models.ImageField(
        _('Foto de Perfil'),
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        help_text='Foto de perfil do usuário'
    )
    tipo_usuario = models.CharField(
        _('Tipo de Usuário'),
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.CLIENTE
    )
    ativo = models.BooleanField(_('Ativo'), default=True)
    is_staff = models.BooleanField(_('Staff'), default=False)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'telefone']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario', 'ativo']),
        ]
    
    def __str__(self):
        return f'{self.nome} ({self.email})'
    
    def get_full_name(self):
        return self.nome
    
    def get_short_name(self):
        return self.nome.split()[0] if self.nome else ''
    
    @property
    def is_cliente(self):
        return self.tipo_usuario == self.TipoUsuario.CLIENTE
    
    @property
    def is_funcionario(self):
        return self.tipo_usuario == self.TipoUsuario.FUNCIONARIO
    
    @property
    def is_administrador(self):
        return self.tipo_usuario == self.TipoUsuario.ADMINISTRADOR

