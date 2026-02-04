# apps/pagamentos/serializers.py
"""
Serializers para o app de pagamentos (LOCAL - sem gateway).
"""
from rest_framework import serializers
from .models import FormaPagamento, TransacaoPagamento


class FormaPagamentoSerializer(serializers.ModelSerializer):
    """
    Serializer de Forma de Pagamento.
    """
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )
    
    class Meta:
        model = FormaPagamento
        fields = [
            'id', 'nome', 'tipo', 'tipo_display', 'descricao',
            'ativo', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao']


class TransacaoPagamentoSerializer(serializers.ModelSerializer):
    """
    Serializer base de Transação de Pagamento.
    """
    forma_pagamento_display = serializers.CharField(
        source='forma_pagamento.nome',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = TransacaoPagamento
        fields = [
            'id', 'agendamento', 'forma_pagamento', 'forma_pagamento_display',
            'valor', 'status', 'status_display', 'valor_recebido', 'troco',
            'pix_qrcode', 'pix_codigo', 'pix_txid', 'numero_transacao',
            'bandeira_cartao', 'ultimos_digitos', 'data_pagamento',
            'observacoes', 'data_criacao'
        ]
        read_only_fields = [
            'id', 'troco', 'pix_qrcode', 'pix_codigo',
            'pix_txid', 'data_criacao'
        ]


class ProcessarPagamentoDinheiroSerializer(serializers.Serializer):
    """
    Serializer para processar pagamento em dinheiro.
    """
    agendamento_id = serializers.IntegerField()
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)
    valor_recebido = serializers.DecimalField(max_digits=10, decimal_places=2)
    observacoes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_valor_recebido(self, value):
        if value < 0:
            raise serializers.ValidationError('Valor recebido não pode ser negativo.')
        return value
    
    def validate(self, attrs):
        if attrs['valor_recebido'] < attrs['valor']:
            raise serializers.ValidationError({
                'valor_recebido': 'Valor recebido insuficiente.'
            })
        return attrs


class ProcessarPagamentoCartaoSerializer(serializers.Serializer):
    """
    Serializer para processar pagamento com cartão.
    """
    agendamento_id = serializers.IntegerField()
    forma_pagamento_id = serializers.IntegerField()
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)
    numero_transacao = serializers.CharField(max_length=100)
    bandeira_cartao = serializers.CharField(max_length=50)
    ultimos_digitos = serializers.CharField(max_length=4)
    observacoes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_ultimos_digitos(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError('Deve conter exatamente 4 dígitos.')
        return value


class ProcessarPagamentoPixSerializer(serializers.Serializer):
    """
    Serializer para processar pagamento via PIX.
    """
    agendamento_id = serializers.IntegerField()
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)
    observacoes = serializers.CharField(required=False, allow_blank=True)


class ConfirmarPagamentoPixSerializer(serializers.Serializer):
    """
    Serializer para confirmar pagamento PIX.
    """
    transacao_id = serializers.IntegerField()
    pix_txid = serializers.CharField(max_length=100, required=False)
