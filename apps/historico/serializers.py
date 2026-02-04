# apps/historico/serializers.py
"""
Serializers para o app de histórico de atendimentos.
"""
from rest_framework import serializers
from .models import HistoricoAtendimento


class HistoricoAtendimentoSerializer(serializers.ModelSerializer):
    """
    Serializer base de Histórico de Atendimento.
    """
    nome_pet = serializers.CharField(source='pet.nome', read_only=True)
    forma_pagamento_display = serializers.CharField(
        source='forma_pagamento.nome',
        read_only=True
    )
    
    class Meta:
        model = HistoricoAtendimento
        fields = [
            'id', 'agendamento', 'pet', 'nome_pet',
            'forma_pagamento', 'forma_pagamento_display',
            'data_atendimento', 'tipo_servico', 'observacoes',
            'valor_pago', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao']


class HistoricoAtendimentoListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de histórico.
    """
    nome_pet = serializers.CharField(source='pet.nome', read_only=True)
    
    class Meta:
        model = HistoricoAtendimento
        fields = [
            'id', 'nome_pet', 'tipo_servico',
            'data_atendimento', 'valor_pago'
        ]
