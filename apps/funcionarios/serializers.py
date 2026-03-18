# apps/funcionarios/serializers.py
"""
Serializers para o app de funcionários.
"""
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import Group
from .models import Funcionario, HorarioTrabalho
from apps.authentication.models import Usuario
from apps.authentication.constants import UserGroups
from apps.authentication.serializers import UsuarioSerializer


class HorarioTrabalhoSerializer(serializers.ModelSerializer):
    """
    Serializer para o Horário de Trabalho.
    """
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = HorarioTrabalho
        fields = ['id', 'funcionario', 'dia_semana', 'dia_semana_display', 'hora_inicio', 'hora_fim', 'ativo']
        read_only_fields = ['id', 'ativo']



class FuncionarioSerializer(serializers.ModelSerializer):
    """
    Serializer base de Funcionário.
    """
    usuario = UsuarioSerializer(read_only=True)
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    total_atendimentos = serializers.IntegerField(read_only=True)
    horarios = HorarioTrabalhoSerializer(source='horarios_trabalho', many=True, read_only=True)
    
    class Meta:
        model = Funcionario
        fields = [
            'id', 'usuario', 'cargo', 'cargo_display',
            'horario_trabalho', 'horarios', 'total_atendimentos',
            'ativo', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'ativo', 'data_criacao', 'data_atualizacao']


class FuncionarioListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de funcionários.
    """
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    
    class Meta:
        model = Funcionario
        fields = [
            'id', 'nome', 'email', 'cargo', 'cargo_display', 'horario_trabalho'
        ]


class FuncionarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de funcionário.
    """
    # Campos do usuário
    email = serializers.EmailField(write_only=True)
    nome = serializers.CharField(write_only=True)
    telefone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    senha = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirmar_senha = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    # Campos do funcionário
    cargo = serializers.ChoiceField(choices=Funcionario.Cargo.choices)
    
    class Meta:
        model = Funcionario
        fields = [
            'email', 'nome', 'telefone', 'senha', 'confirmar_senha',
            'cargo'
        ]
    
    def validate(self, attrs):
        if attrs['senha'] != attrs.pop('confirmar_senha'):
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        # Criar usuário
        usuario_data = {
            'email': validated_data.pop('email'),
            'nome': validated_data.pop('nome'),
            'telefone': validated_data.pop('telefone', ''),
            'senha': validated_data.pop('senha'),
        }
        usuario = Usuario.objects.create_user(**usuario_data)
        
        # Adicionar ao grupo FUNCIONARIO
        grupo_funcionario, _ = Group.objects.get_or_create(name=UserGroups.FUNCIONARIO)
        usuario.groups.add(grupo_funcionario)
        
        # Criar funcionário com um dummy para horario_trabalho exigido pelo model
        funcionario = Funcionario.objects.create(
            usuario=usuario,
            horario_trabalho='A definir',
            **validated_data
        )
        
        return funcionario


class FuncionarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de funcionário.
    """
    nome = serializers.CharField(source='usuario.nome', required=False)
    telefone = serializers.CharField(source='usuario.telefone', required=False, allow_blank=True)
    email = serializers.EmailField(source='usuario.email', required=False)
    
    class Meta:
        model = Funcionario
        fields = [
            'nome', 'telefone', 'email', 'cargo'
        ]
    
    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('usuario', {})
        if usuario_data:
            for attr, value in usuario_data.items():
                setattr(instance.usuario, attr, value)
            instance.usuario.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
