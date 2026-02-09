# apps/clientes/services.py
"""
Services para operações de clientes.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from .models import Cliente
from apps.authentication.models import Usuario
from apps.authentication.constants import UserGroups


class ClienteService:
    """
    Service para operações de cliente.
    """
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados_usuario, dados_cliente):
        """
        Cria um cliente completo (usuário + cliente).
        Adiciona automaticamente ao grupo CLIENTE.
        
        Args:
            dados_usuario: dict com dados do usuário (email, nome, telefone, senha)
            dados_cliente: dict com dados do cliente (cpf, endereco, cidade, estado, cep)
        
        Returns:
            Cliente: Instância do cliente criado
        """
        email = dados_usuario.get('email')
        cpf = dados_cliente.get('cpf')

        # Verificar se email já existe
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Já existe um usuário com este email.')
        
        # Verificar se CPF já existe
        if Cliente.objects.filter(cpf=cpf, ativo=True).exists():
            raise ValidationError('Já existe um cliente com este CPF.')
        
        # Criar usuário
        usuario = Usuario.objects.create_user(
            email=email,
            nome=dados_usuario['nome'],
            telefone=dados_usuario['telefone'],
            senha=dados_usuario['senha']
        )
        
        # Adicionar ao grupo CLIENTE
        grupo_cliente, _ = Group.objects.get_or_create(name=UserGroups.CLIENTE)
        usuario.groups.add(grupo_cliente)
        
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
        if not hasattr(usuario, 'cliente'):
             raise ValidationError('Cliente não encontrado para este usuário.')
        return usuario.cliente
    
    @staticmethod
    def atualizar_cliente(cliente, dados):
        """
        Atualiza dados do cliente de forma segura.
        Ignora campos que não devem ser atualizados via service genérico.
        """
        # Lista de campos permitidos para atualização
        campos_permitidos = {'endereco', 'cidade', 'estado', 'cep', 'telefone'}
        
        # Atualiza campos do Cliente
        alterado = False
        for campo, valor in dados.items():
            if campo in campos_permitidos and hasattr(cliente, campo):
                setattr(cliente, campo, valor)
                alterado = True
                
        # Atualiza campos do Usuário se necessário (ex: telefone)
        if 'telefone' in dados:
             cliente.usuario.telefone = dados['telefone']
             cliente.usuario.save()

        if alterado:
            cliente.save()
            
        return cliente

