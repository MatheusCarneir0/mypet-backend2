"""
Serializers do app users.
"""
import re
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.users.models import User
from core.utils import validate_cpf, format_phone_number


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo User.
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'telefone',
            'tipo_usuario',
            'ativo',
            'data_cadastro',
            'date_joined',
        ]
        read_only_fields = ['id', 'data_cadastro', 'date_joined', 'tipo_usuario']
    
    def validate_email(self, value):
        """Valida formato de email."""
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Email inválido.")
        
        # Verificar se email já existe (exceto para o próprio usuário)
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk if user else None).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        return value.lower()
    
    def validate_telefone(self, value):
        """Valida e formata número de telefone."""
        if not value:
            return value
        
        # Remove caracteres não numéricos
        phone_cleaned = format_phone_number(value)
        
        # Valida formato brasileiro (10 ou 11 dígitos)
        if len(phone_cleaned) < 10 or len(phone_cleaned) > 11:
            raise serializers.ValidationError(
                "Telefone deve ter 10 ou 11 dígitos (DDD + número)."
            )
        
        return phone_cleaned


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuário.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Senha deve ter no mínimo 8 caracteres, incluindo letras e números."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'telefone',
            'tipo_usuario',
        ]
    
    def validate_email(self, value):
        """Valida formato de email e verifica unicidade."""
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Email inválido.")
        
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        return value.lower()
    
    def validate_username(self, value):
        """Valida username."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        
        if len(value) < 3:
            raise serializers.ValidationError("Nome de usuário deve ter no mínimo 3 caracteres.")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Nome de usuário pode conter apenas letras, números e underscore."
            )
        
        return value
    
    def validate_password(self, value):
        """Valida força da senha."""
        if len(value) < 8:
            raise serializers.ValidationError("Senha deve ter no mínimo 8 caracteres.")
        
        # Verifica se tem pelo menos uma letra
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Senha deve conter pelo menos uma letra.")
        
        # Verifica se tem pelo menos um número
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Senha deve conter pelo menos um número.")
        
        return value
    
    def validate_telefone(self, value):
        """Valida e formata número de telefone."""
        if not value:
            return value
        
        phone_cleaned = format_phone_number(value)
        
        if len(phone_cleaned) < 10 or len(phone_cleaned) > 11:
            raise serializers.ValidationError(
                "Telefone deve ter 10 ou 11 dígitos (DDD + número)."
            )
        
        return phone_cleaned
    
    def validate_tipo_usuario(self, value):
        """Valida tipo de usuário."""
        valid_types = [choice[0] for choice in User.TipoUsuario.choices]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Tipo de usuário inválido. Opções: {', '.join(valid_types)}"
            )
        return value
    
    def validate(self, attrs):
        """Validações gerais."""
        # Valida se as senhas coincidem
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Cria um novo usuário."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de usuário.
    """
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'telefone',
        ]
    
    def validate_email(self, value):
        """Valida formato de email."""
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Email inválido.")
        
        # Verificar se email já existe (exceto para o próprio usuário)
        user = self.instance
        if User.objects.filter(email=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        return value.lower()
    
    def validate_telefone(self, value):
        """Valida e formata número de telefone."""
        if not value:
            return value
        
        phone_cleaned = format_phone_number(value)
        
        if len(phone_cleaned) < 10 or len(phone_cleaned) > 11:
            raise serializers.ValidationError(
                "Telefone deve ter 10 ou 11 dígitos (DDD + número)."
            )
        
        return phone_cleaned

