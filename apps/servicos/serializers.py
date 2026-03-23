# apps/servicos/serializers.py
"""
Serializers para o app de serviços.
"""
from rest_framework import serializers
from .models import Servico, ServicoCargo


class ServicoCargoSerializer(serializers.ModelSerializer):
    """Serializer para os cargos vinculados a um serviço."""
    cargo_display = serializers.CharField(
        source='get_cargo_display',
        read_only=True
    )

    class Meta:
        model = ServicoCargo
        fields = ['cargo', 'cargo_display']


class ServicoSerializer(serializers.ModelSerializer):
    """
    Serializer completo de Serviço (read).
    """
    cargos = ServicoCargoSerializer(many=True, read_only=True)

    class Meta:
        model = Servico
        fields = [
            'id', 'nome', 'descricao', 'preco',
            'duracao_minutos', 'cargos', 'ativo',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']


class ServicoListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de serviços.
    """
    cargos = ServicoCargoSerializer(many=True, read_only=True)

    class Meta:
        model = Servico
        fields = [
            'id', 'nome', 'descricao', 'preco',
            'duracao_minutos', 'cargos'
        ]


class ServicoCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de serviço.
    Aceita `cargos` como lista de strings de cargo (ex: ["TOSADOR", "ATENDENTE"]).
    """
    cargos = serializers.ListField(
        child=serializers.ChoiceField(choices=[c[0] for c in ServicoCargo.CARGO_CHOICES]),
        write_only=True,
        required=True,
        min_length=1,
        help_text='Lista de cargos que realizam este serviço. Ex: ["TOSADOR", "VETERINARIO"]'
    )

    class Meta:
        model = Servico
        fields = [
            'id', 'nome', 'descricao', 'preco',
            'duracao_minutos', 'cargos'
        ]
        read_only_fields = ['id']

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError('O preço não pode ser negativo.')
        return value

    def validate_duracao_minutos(self, value):
        if value <= 0:
            raise serializers.ValidationError('A duração deve ser maior que zero.')
        if value > 480:  # 8 horas
            raise serializers.ValidationError('Duração muito longa (máximo 480 minutos).')
        return value

    def _salvar_cargos(self, servico, cargos):
        """Remove os cargos antigos e salva os novos."""
        servico.cargos.all().delete()
        ServicoCargo.objects.bulk_create([
            ServicoCargo(servico=servico, cargo=cargo)
            for cargo in set(cargos)
        ])

    def create(self, validated_data):
        cargos = validated_data.pop('cargos')
        servico = super().create(validated_data)
        self._salvar_cargos(servico, cargos)
        return servico

    def update(self, instance, validated_data):
        cargos = validated_data.pop('cargos', None)
        servico = super().update(instance, validated_data)
        if cargos is not None:
            self._salvar_cargos(servico, cargos)
        return servico
