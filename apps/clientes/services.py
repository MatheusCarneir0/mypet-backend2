# apps/clientes/services.py
"""
Services para operações de clientes.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Cliente
from apps.authentication.models import Usuario


class ClienteService:
    """
    Service para operações de cliente.
    """
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados_usuario, dados_cliente):
        """
        Cria um cliente completo (usuário + cliente).
        
        Args:
            dados_usuario: dict com dados do usuário
            dados_cliente: dict com dados do cliente
        
        Returns:
            Cliente: Instância do cliente criado
        """
        # Verificar se email já existe
        if Usuario.objects.filter(email=dados_usuario['email']).exists():
            raise ValidationError('Já existe um usuário com este email.')
        
        # Verificar se CPF já existe
        if Cliente.objects.filter(cpf=dados_cliente['cpf'], ativo=True).exists():
            raise ValidationError('Já existe um cliente com este CPF.')
        
        # Criar usuário
        usuario = Usuario.objects.create_user(
            email=dados_usuario['email'],
            nome=dados_usuario['nome'],
            telefone=dados_usuario['telefone'],
            senha=dados_usuario['senha'],
            tipo_usuario=Usuario.TipoUsuario.CLIENTE
        )
        
        # Criar cliente
        cliente = Cliente.objects.create(
            usuario=usuario,
            **dados_cliente
        )
        
        return cliente
    
    @staticmethod
    def obter_cliente_por_usuario(usuario):
        """
        Obtém o cliente associado a um usuário.
        """
        try:
            return usuario.cliente
        except Cliente.DoesNotExist:
            raise ValidationError('Cliente não encontrado para este usuário.')
    
    @staticmethod
    def atualizar_cliente(cliente, dados):
        """
        Atualiza dados do cliente.
        """
        for campo, valor in dados.items():
            setattr(cliente, campo, valor)
        
        cliente.save()
        return cliente

