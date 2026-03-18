# apps/historico/serializers.py
"""
Serializers para o app de histórico de atendimentos.
"""
from rest_framework import serializers
from .models import HistoricoAtendimento


class HistoricoAtendimentoSerializer(serializers.ModelSerializer):
    """
    Serializer de detalhe de Histórico de Atendimento.
    """
    nome_pet = serializers.CharField(source='pet.nome', read_only=True)
    nome_cliente = serializers.CharField(
        source='agendamento.cliente.usuario.get_full_name', read_only=True)
    nome_funcionario = serializers.SerializerMethodField()
    status = serializers.CharField(source='agendamento.status', read_only=True)
    forma_pagamento_display = serializers.CharField(
        source='forma_pagamento.nome',
        read_only=True,
        default=None
    )
    
    class Meta:
        model = HistoricoAtendimento
        fields = [
            'id', 'agendamento', 'pet', 'nome_pet',
            'nome_cliente', 'nome_funcionario', 'status',
            'forma_pagamento', 'forma_pagamento_display',
            'data_atendimento', 'tipo_servico', 'observacoes',
            'valor_pago', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao']

    def get_nome_funcionario(self, obj):
        func = getattr(obj.agendamento, 'funcionario', None)
        if func:
            return func.usuario.get_full_name()
        return None


class HistoricoAtendimentoListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de histórico.
    """
    nome_pet = serializers.CharField(source='pet.nome', read_only=True)
    nome_cliente = serializers.CharField(
        source='agendamento.cliente.usuario.get_full_name', read_only=True)
    nome_funcionario = serializers.SerializerMethodField()
    status = serializers.CharField(source='agendamento.status', read_only=True)

    class Meta:
        model = HistoricoAtendimento
        fields = [
            'id', 'nome_pet', 'nome_cliente', 'nome_funcionario',
            'tipo_servico', 'data_atendimento', 'valor_pago',
            'observacoes', 'status'
        ]

    def get_nome_funcionario(self, obj):
        func = getattr(obj.agendamento, 'funcionario', None)
        if func:
            return func.usuario.get_full_name()
        return None
