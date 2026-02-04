# apps/authentication/services.py
"""
Services para autenticação e gerenciamento de usuários.
"""
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario


class AuthenticationService:
    """
    Service para operações de autenticação.
    """
    
    @staticmethod
    def autenticar_usuario(email, senha):
        """
        Autentica um usuário.
        """
        from django.contrib.auth import authenticate
        
        usuario = authenticate(username=email, password=senha)
        
        if usuario is None:
            return None, None
        
        if not usuario.ativo:
            raise ValidationError('Conta inativa. Entre em contato com o administrador.')
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(usuario)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return usuario, tokens
    
    @staticmethod
    def alterar_senha(usuario, senha_atual, senha_nova):
        """
        Altera a senha de um usuário.
        """
        if not usuario.check_password(senha_atual):
            raise ValidationError('Senha atual incorreta.')
        
        usuario.set_password(senha_nova)
        usuario.save()
        
        return True
    
    @staticmethod
    def desativar_usuario(usuario):
        """
        Desativa um usuário (soft delete).
        """
        usuario.ativo = False
        usuario.save()
        return True

