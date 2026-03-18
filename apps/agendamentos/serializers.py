# apps/agendamentos/serializers.py
"""
Serializers para o app de agendamentos.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Agendamento
from apps.pets.serializers import PetListSerializer
from apps.servicos.serializers import ServicoSerializer, ServicoListSerializer
from apps.funcionarios.serializers import FuncionarioListSerializer
from apps.clientes.models import Cliente
from drf_spectacular.utils import extend_schema_field


class FormaPagamentoNestedSerializer(serializers.Serializer):
    """Serializer inline para forma de pagamento no agendamento."""
    id = serializers.IntegerField()
    nome = serializers.CharField()
    tipo = serializers.CharField()


class AgendamentoSerializer(serializers.ModelSerializer):
    """
    Serializer base de Agendamento.
    """
    pet = PetListSerializer(read_only=True)
    servico = ServicoSerializer(read_only=True)
    funcionario = FuncionarioListSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'pet', 'servico', 'funcionario',
            'data_hora', 'status', 'observacoes', 'status_display',
            'forma_pagamento', 'status_pagamento', 'valor_pago',
            'data_criacao', 'data_atualizacao'
        ]


class AgendamentoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de agendamentos.
    """
    pet = PetListSerializer(read_only=True)
    servico = ServicoListSerializer(read_only=True)
    cliente_nome = serializers.CharField(source='cliente.usuario.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    forma_pagamento = FormaPagamentoNestedSerializer(read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'pet',
            'servico', 'funcionario', 'data_hora',
            'status', 'status_display', 'forma_pagamento',
            'status_pagamento', 'valor_pago', 'data_criacao'
        ]


class AgendamentoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar agendamento.
    Permite Admin/Funcionário especificar cliente, ou Cliente criar para si.
    """
    cliente_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente_id', 'pet', 'servico', 'funcionario',
            'data_hora', 'forma_pagamento', 'observacoes'
        ]
        read_only_fields = ['id']

    def validate_cliente_id(self, value):
        """Valida se o cliente existe."""
        try:
            cliente = Cliente.objects.get(id=value)
            return cliente
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("Cliente não encontrado.")

    def validate(self, data):
        """Validações gerais."""
        request = self.context.get('request')
        
        if 'cliente_id' in data:
            cliente = data.pop('cliente_id')
        else:
            try:
                cliente = request.user.cliente
                data['cliente'] = cliente
            except AttributeError:
                raise serializers.ValidationError(
                    "Apenas clientes podem criar agendamento sem especificar cliente_id."
                )
        
        if isinstance(cliente, int):
            data['cliente'] = Cliente.objects.get(id=cliente)
        else:
            data['cliente'] = cliente

        pet = data.get('pet')
        if pet and pet.cliente != data['cliente']:
            raise serializers.ValidationError(
                "O pet não pertence a este cliente."
            )

        return data

    def create(self, validated_data):
        """Cria o agendamento via Service Layer (com conflict detection e alocação)."""
        from apps.agendamentos.services import AgendamentoService
        return AgendamentoService.criar_agendamento(
            cliente=validated_data['cliente'],
            pet_id=validated_data['pet'].id,
            servico_id=validated_data['servico'].id,
            data_hora=validated_data['data_hora'],
            forma_pagamento_id=validated_data['forma_pagamento'].id,
            observacoes=validated_data.get('observacoes', ''),
        )


class AgendamentoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualizar agendamento.
    """
    class Meta:
        model = Agendamento
        fields = [
            'pet', 'servico', 'funcionario',
            'data_hora', 'forma_pagamento', 'observacoes'
        ]


class AgendamentoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado de agendamento.
    """
    pet = PetListSerializer(read_only=True)
    servico = ServicoSerializer(read_only=True)
    funcionario = FuncionarioListSerializer(read_only=True)
    cliente_nome = serializers.CharField(source='cliente.usuario.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    forma_pagamento = FormaPagamentoNestedSerializer(read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'pet', 'servico',
            'funcionario', 'data_hora', 'status', 'status_display',
            'forma_pagamento', 'status_pagamento', 'valor_pago',
            'observacoes', 'data_criacao', 'data_atualizacao'
        ]


class CancelarAgendamentoSerializer(serializers.Serializer):
    """Serializer para cancelar agendamento."""
    motivo = serializers.CharField(max_length=500, required=False)


class ReagendarAgendamentoSerializer(serializers.Serializer):
    """Serializer para reagendar agendamento."""
    data_hora = serializers.DateTimeField()
    observacoes = serializers.CharField(max_length=1000, required=False)


class IniciarAgendamentoSerializer(serializers.Serializer):
    """Serializer para iniciar atendimento."""
    observacoes = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class ConcluirAgendamentoSerializer(serializers.Serializer):
    """Serializer para concluir agendamento."""
    observacoes = serializers.CharField(max_length=1000, required=False, default='', allow_blank=True)
    valor_pago = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    forma_pagamento_id = serializers.IntegerField(required=False, allow_null=True)


class AtualizarStatusAgendamentoSerializer(serializers.Serializer):
    """Serializer para atualizar status."""
    status = serializers.ChoiceField(choices=Agendamento.Status.choices)
    observacoes = serializers.CharField(max_length=1000, required=False)