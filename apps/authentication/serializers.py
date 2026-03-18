# apps/authentication/serializers.py
"""
Serializers para autenticação e gerenciamento de usuários.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from .models import Usuario
from drf_spectacular.utils import extend_schema_field


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer base de Usuario.
    Inclui grupos do usuário para controle de permissões.
    """
    groups = serializers.SerializerMethodField()
    cliente_id = serializers.SerializerMethodField()
    # #9: SerializerMethodField com type hint para resolver warning do Swagger
    ativo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome', 'telefone', 'foto',
            'groups', 'cliente_id', 'ativo', 'data_criacao'
        ]
        read_only_fields = ['id', 'groups', 'cliente_id', 'data_criacao']

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_groups(self, obj):
        """Retorna lista de nomes dos grupos do usuário."""
        return obj.get_grupos()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_cliente_id(self, obj):
        """Retorna o ID do perfil de cliente, se existir."""
        try:
            return obj.cliente.id
        except Exception:
            return None

    @extend_schema_field(serializers.BooleanField())
    def get_ativo(self, obj):
        """Retorna se o usuário está ativo (usa campo is_active do DB)."""
        return obj.is_active



class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuário.
    """
    senha = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirmar_senha = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'nome', 'telefone', 
            'senha', 'confirmar_senha'
        ]
    
    def validate(self, attrs):
        """
        Validação customizada.
        """
        # Validar senhas
        if attrs['senha'] != attrs.pop('confirmar_senha'):
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        
        # Validar força da senha
        try:
            validate_password(attrs['senha'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'senha': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Criar usuário com senha hash.
        """
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(
            senha=senha,
            **validated_data
        )
        return usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para JWT token.
    Adiciona informações extras ao token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicionar claims customizados
        token['nome'] = user.nome
        token['email'] = user.email
        token['groups'] = user.get_grupos()  # Lista de grupos ao invés de tipo_usuario
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Adicionar dados extras à resposta
        # data['usuario'] = {
        #     'id': self.user.id,
        #     'email': self.user.email,
        #     'nome': self.user.nome,
        #     'groups': self.user.get_grupos(),  # Lista de grupos ao invés de tipo_usuario
        # }
        
        return data


class AlterarSenhaSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha.
    """
    senha_atual = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    senha_nova = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    confirmar_senha_nova = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['senha_nova'] != attrs['confirmar_senha_nova']:
            raise serializers.ValidationError({
                'confirmar_senha_nova': 'As senhas não coincidem.'
            })
        
        try:
            validate_password(attrs['senha_nova'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'senha_nova': list(e.messages)
            })
        
        return attrs


class UploadFotoSerializer(serializers.Serializer):
    """
    Serializer para upload de foto de perfil.
    """
    foto = serializers.ImageField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitar redefinição de senha via email.
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmar nova senha usando uid + token.
    """
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    senha_nova = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
    )
    confirmar_senha = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        if attrs['senha_nova'] != attrs['confirmar_senha']:
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        try:
            validate_password(attrs['senha_nova'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'senha_nova': list(e.messages)})
        return attrs
