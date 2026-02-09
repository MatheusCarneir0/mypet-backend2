# apps/authentication/signals.py
"""
Signals para o app authentication.
Cria grupos automaticamente após migrations.
"""
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """
    Cria os grupos de usuário automaticamente após migrations.
    
    Grupos criados:
    - CLIENTE: Usuários clientes do pet shop
    - FUNCIONARIO: Funcionários (atendentes, tosadores, veterinários)
    - ADMINISTRADOR: Administradores do sistema
    """
    # Só executa para o app authentication
    if sender.name == 'apps.authentication':
        grupos = ['CLIENTE', 'FUNCIONARIO', 'ADMINISTRADOR']
        
        for nome_grupo in grupos:
            grupo, created = Group.objects.get_or_create(name=nome_grupo)
            if created:
                logger.info(f"✅ Grupo '{nome_grupo}' criado com sucesso.")
            else:
                logger.debug(f"ℹ️ Grupo '{nome_grupo}' já existe.")
