# apps/funcionarios/services.py
"""
Services para operações de funcionários.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from .models import Funcionario
from apps.authentication.models import Usuario


class FuncionarioService:
    """
    Service para operações de funcionário.
    Apenas administradores podem criar funcionários.
    """
    
    @staticmethod
    @transaction.atomic
    def criar_funcionario(dados_usuario, dados_funcionario):
        """
        Cria um funcionário completo (usuário + funcionário).
        Adiciona automaticamente ao grupo FUNCIONARIO.
        
        Args:
            dados_usuario: dict com dados do usuário (email, nome, telefone, senha)
            dados_funcionario: dict com dados do funcionário (cargo, horario_trabalho)
        
        Returns:
            Funcionario: Instância do funcionário criado
        """
        # Verificar se email já existe
        if Usuario.objects.filter(email=dados_usuario['email']).exists():
            raise ValidationError('Já existe um usuário com este email.')
        
        # Criar usuário
        usuario = Usuario.objects.create_user(
            email=dados_usuario['email'],
            nome=dados_usuario['nome'],
            telefone=dados_usuario['telefone'],
            senha=dados_usuario['senha']
        )
        
        # Adicionar ao grupo FUNCIONARIO
        grupo_funcionario, _ = Group.objects.get_or_create(name='FUNCIONARIO')
        usuario.groups.add(grupo_funcionario)
        
        # Criar funcionário
        funcionario = Funcionario.objects.create(
            usuario=usuario,
            **dados_funcionario
        )
        
        return funcionario
    
    @staticmethod
    def obter_funcionario_por_usuario(usuario):
        """
        Obtém o funcionário associado a um usuário.
        """
        try:
            return usuario.funcionario
        except Funcionario.DoesNotExist:
            raise ValidationError('Funcionário não encontrado para este usuário.')
    
    @staticmethod
    def atualizar_funcionario(funcionario, dados):
        """
        Atualiza dados do funcionário.
        """
        for campo, valor in dados.items():
            setattr(funcionario, campo, valor)
        
        funcionario.save()
        return funcionario
