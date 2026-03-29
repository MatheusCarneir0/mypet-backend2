# apps/pets/serializers.py
"""
Serializers para o app de pets.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Pet
from apps.clientes.models import Cliente


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer base de Pet.
    """
    nome_cliente = serializers.CharField(
        source='cliente.usuario.nome',
        read_only=True
    )
    porte_display = serializers.CharField(
        source='get_porte_display',
        read_only=True
    )
    especie_display = serializers.CharField(
        source='get_especie_display',
        read_only=True
    )
    total_atendimentos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Pet
        fields = [
            'id', 'cliente', 'nome_cliente', 'nome', 'especie',
            'especie_display', 'raca', 'idade', 'data_nascimento', 'peso', 'porte',
            'porte_display', 'foto', 'observacoes', 'total_atendimentos',
            'ativo', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = [
            'id', 'porte', 'porte_display', 'total_atendimentos',
            'ativo', 'data_criacao', 'data_atualizacao'
        ]


class PetListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de pets.
    """
    nome_cliente = serializers.CharField(
        source='cliente.usuario.nome',
        read_only=True
    )
    especie_display = serializers.CharField(
        source='get_especie_display',
        read_only=True
    )
    porte_display = serializers.CharField(
        source='get_porte_display',
        read_only=True
    )
    
    class Meta:
        model = Pet
        fields = [
            'id', 'cliente', 'nome', 'nome_cliente', 'especie_display',
            'raca', 'idade', 'data_nascimento', 'peso', 'porte_display', 'foto'
        ]


class PetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de pet.
    """
    class Meta:
        model = Pet
        fields = [
            'id', 'cliente', 'nome', 'especie', 'raca',
            'idade', 'data_nascimento', 'peso', 'foto', 'observacoes'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'cliente': {'required': False},
        }
    
    def validate_cliente(self, value):
        """
        Validar que o cliente está ativo.
        """
        if not value.ativo:
            raise serializers.ValidationError(
                'Cliente inativo. Não é possível cadastrar pets.'
            )
        return value
    
    def validate(self, data):
        """
        Se o usuário é cliente, ignora qualquer cliente_id enviado
        (será forçado no perform_create da view).
        """
        request = self.context.get('request')
        if request and request.user.is_cliente:
            data.pop('cliente', None)
        elif 'cliente' not in data:
            raise serializers.ValidationError(
                {'cliente': 'Este campo é obrigatório para funcionários/admin.'}
            )
        return data
    
    def validate_peso(self, value):
        """
        Validar peso do pet.
        """
        if value <= 0:
            raise serializers.ValidationError('O peso deve ser maior que zero.')
        if value > 200:
            raise serializers.ValidationError('Peso muito alto. Verifique o valor.')
        return value


class PetUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de pet.
    """
    class Meta:
        model = Pet
        fields = [
            'nome', 'raca', 'idade', 'data_nascimento', 'peso',
            'foto', 'observacoes'
        ]


class PetDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado de pet com histórico.
    """
    cliente = serializers.SerializerMethodField()
    especie_display = serializers.CharField(
        source='get_especie_display',
        read_only=True
    )
    porte_display = serializers.CharField(
        source='get_porte_display',
        read_only=True
    )
    historico_recente = serializers.SerializerMethodField()
    
    class Meta:
        model = Pet
        fields = [
            'id', 'cliente', 'nome', 'especie', 'especie_display',
            'raca', 'idade', 'data_nascimento', 'peso', 'porte', 'porte_display',
            'foto', 'observacoes', 'historico_recente',
            'total_atendimentos', 'ativo', 'data_criacao'
        ]
    
    @extend_schema_field(dict)
    def get_cliente(self, obj):
        """
        Retornar dados resumidos do cliente.
        """
        return {
            'id': obj.cliente.id,
            'nome': obj.cliente.usuario.nome,
            'email': obj.cliente.usuario.email,
            'telefone': obj.cliente.usuario.telefone,
        }
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_historico_recente(self, obj):
        """
        Retornar últimos 5 atendimentos.
        """
        from apps.historico.serializers import HistoricoAtendimentoListSerializer
        historico = obj.historico_atendimentos.all()[:5]
        return HistoricoAtendimentoListSerializer(historico, many=True).data
