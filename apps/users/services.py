"""
Services do app users (lógica de negócio).
"""
import logging
from typing import Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """
    Service para operações relacionadas a usuários.
    
    Esta classe centraliza a lógica de negócio relacionada a usuários,
    garantindo consistência e reutilização de código.
    """
    
    @staticmethod
    def get_user_by_id(user_id: str, active_only: bool = True) -> User:
        """
        Busca um usuário por ID.
        
        Args:
            user_id: UUID do usuário
            active_only: Se True, retorna apenas usuários ativos
            
        Returns:
            Instância do User
            
        Raises:
            NotFoundError: Se o usuário não for encontrado
        """
        try:
            queryset = User.objects.filter(id=user_id)
            if active_only:
                queryset = queryset.filter(ativo=True)
            user = queryset.get()
            logger.debug(f"Usuário encontrado: {user.username} (ID: {user_id})")
            return user
        except User.DoesNotExist:
            logger.warning(f"Tentativa de buscar usuário inexistente: {user_id}")
            raise NotFoundError(f"Usuário com ID {user_id} não encontrado.")
    
    @staticmethod
    def get_user_by_email(email: str, active_only: bool = True) -> Optional[User]:
        """
        Busca um usuário por email.
        
        Args:
            email: Email do usuário (será normalizado para lowercase)
            active_only: Se True, retorna apenas usuários ativos
            
        Returns:
            Instância do User ou None
        """
        if not email:
            return None
        
        email = email.lower().strip()
        try:
            queryset = User.objects.filter(email=email)
            if active_only:
                queryset = queryset.filter(ativo=True)
            user = queryset.get()
            logger.debug(f"Usuário encontrado por email: {user.username}")
            return user
        except User.DoesNotExist:
            logger.debug(f"Usuário não encontrado por email: {email}")
            return None
        except User.MultipleObjectsReturned:
            logger.error(f"Múltiplos usuários encontrados com email: {email}")
            # Retorna o primeiro ativo se houver
            return queryset.filter(ativo=True).first() if active_only else queryset.first()
    
    @staticmethod
    @transaction.atomic
    def deactivate_user(user_id: str) -> User:
        """
        Desativa um usuário de forma atômica.
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            Instância do User desativado
            
        Raises:
            NotFoundError: Se o usuário não for encontrado
            ValidationError: Se tentar desativar um admin quando é o último admin
        """
        user = UserService.get_user_by_id(user_id, active_only=False)
        
        # Validações de negócio
        if not user.ativo:
            logger.warning(f"Tentativa de desativar usuário já inativo: {user.username}")
            return user
        
        # Verificar se é o último admin ativo (proteção)
        if user.is_admin:
            admin_count = User.objects.get_admins().count()
            if admin_count <= 1:
                logger.error(f"Tentativa de desativar último admin: {user.username}")
                raise ValidationError(
                    "Não é possível desativar o último administrador do sistema."
                )
        
        user.deactivate()
        logger.info(f"Usuário desativado com sucesso: {user.username} (ID: {user_id})")
        return user
    
    @staticmethod
    @transaction.atomic
    def activate_user(user_id: str) -> User:
        """
        Ativa um usuário de forma atômica.
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            Instância do User ativado
            
        Raises:
            NotFoundError: Se o usuário não for encontrado
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Tentativa de ativar usuário inexistente: {user_id}")
            raise NotFoundError(f"Usuário com ID {user_id} não encontrado.")
        
        if user.ativo:
            logger.debug(f"Usuário já está ativo: {user.username}")
            return user
        
        user.activate()
        logger.info(f"Usuário ativado com sucesso: {user.username} (ID: {user_id})")
        return user
    
    @staticmethod
    def check_email_exists(email: str, exclude_user_id: Optional[str] = None) -> bool:
        """
        Verifica se um email já está em uso.
        
        Args:
            email: Email a verificar
            exclude_user_id: ID do usuário a excluir da verificação
            
        Returns:
            True se o email existe, False caso contrário
        """
        email = email.lower().strip() if email else None
        if not email:
            return False
        
        queryset = User.objects.filter(email=email)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        
        return queryset.exists()
    
    @staticmethod
    def check_username_exists(username: str, exclude_user_id: Optional[str] = None) -> bool:
        """
        Verifica se um username já está em uso.
        
        Args:
            username: Username a verificar
            exclude_user_id: ID do usuário a excluir da verificação
            
        Returns:
            True se o username existe, False caso contrário
        """
        if not username:
            return False
        
        queryset = User.objects.filter(username=username)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        
        return queryset.exists()

