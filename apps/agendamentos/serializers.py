# apps/agendamentos/serializers.py
"""
Serializers para o app de agendamentos.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Agendamento
from apps.pets.serializers import PetListSerializer
from apps.servicos.serializers import ServicoSerializer
from apps.funcionarios.serializers import FuncionarioListSerializer
from drf_spectacular.utils import extend_schema_field


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
    pode_cancelar = serializers.BooleanField(read_only=True)
    pode_iniciar = serializers.BooleanField(read_only=True)
    pode_concluir = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'pet', 'servico', 'funcionario',
            'data_hora', 'status', 'status_display', 'observacoes',
            'pode_cancelar', 'pode_iniciar', 'pode_concluir',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'cliente', 'data_criacao', 'data_atualizacao']


class AgendamentoListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de agendamentos.
    """
    nome_pet = serializers.CharField(source='pet.nome', read_only=True)
    nome_cliente = serializers.CharField(
        source='cliente.usuario.nome',
        read_only=True
    )
    tipo_servico = serializers.CharField(
        source='servico.get_tipo_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'nome_cliente', 'nome_pet', 'tipo_servico',
            'data_hora', 'status', 'status_display'
        ]


class AgendamentoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de agendamento.
    """
    class Meta:
        model = Agendamento
        fields = [
            'pet', 'servico', 'data_hora', 'forma_pagamento', 'observacoes'
        ]
    
    def validate_data_hora(self, value):
        """
        Validar que a data/hora é futura.
        """
        if value < timezone.now():
            raise serializers.ValidationError(
                'Não é possível agendar para uma data/hora no passado.'
            )
        
        # Validar horário comercial (8h às 18h)
        if value.hour < 8 or value.hour >= 18:
            raise serializers.ValidationError(
                'Horário fora do expediente. Atendimento de 08:00 às 18:00.'
            )
        
        # Validar que não é domingo
        if value.weekday() == 6:
            raise serializers.ValidationError(
                'Não atendemos aos domingos.'
            )
        
        return value
    
    def validate(self, attrs):
        """
        Validações cruzadas.
        """
        pet = attrs.get('pet')
        cliente = self.context['request'].user.cliente
        
        # Validar que o pet pertence ao cliente
        if pet.cliente != cliente:
            raise serializers.ValidationError({
                'pet': 'O pet selecionado não pertence a você.'
            })
        
        return attrs


class AgendamentoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de agendamento (reagendamento).
    """
    class Meta:
        model = Agendamento
        fields = ['data_hora', 'observacoes']
    
    def validate_data_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                'Não é possível reagendar para uma data/hora no passado.'
            )
        return value


class AgendamentoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado de agendamento.
    """
    pet = PetListSerializer(read_only=True)
    servico = ServicoSerializer(read_only=True)
    funcionario = FuncionarioListSerializer(read_only=True)
    cliente = serializers.SerializerMethodField()
    forma_pagamento = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'pet', 'servico', 'funcionario',
            'forma_pagamento', 'data_hora', 'status', 'status_display', 
            'observacoes', 'data_criacao', 'data_atualizacao'
        ]
    
    @extend_schema_field(dict)
    def get_cliente(self, obj):
        return {
            'id': obj.cliente.id,
            'nome': obj.cliente.usuario.nome,
            'email': obj.cliente.usuario.email,
            'telefone': obj.cliente.usuario.telefone,
        }
    
    @extend_schema_field(dict)
    def get_forma_pagamento(self, obj):
        if obj.forma_pagamento:
            return {
                'id': obj.forma_pagamento.id,
                'nome': obj.forma_pagamento.nome,
                'tipo': obj.forma_pagamento.tipo,
                'tipo_display': obj.forma_pagamento.get_tipo_display(),
            }
        return None


class CancelarAgendamentoSerializer(serializers.Serializer):
    """
    Serializer para cancelar agendamento.
    """
    motivo = serializers.CharField(required=True, help_text="Motivo do cancelamento")


class ReagendarAgendamentoSerializer(serializers.Serializer):
    """
    Serializer para reagendar agendamento.
    """
    data_hora = serializers.DateTimeField(required=True, help_text="Nova data e hora")

    def validate_data_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                'Não é possível reagendar para uma data/hora no passado.'
            )
        return value



class IniciarAgendamentoSerializer(serializers.Serializer):
    """
    Serializer para iniciar um agendamento.
    """
    funcionario_id = serializers.IntegerField(required=False)


class ConcluirAgendamentoSerializer(serializers.Serializer):
    """
    Serializer para concluir um agendamento.
    Captura observacoes e valor_pago para registrar no histórico (UC15).
    """
    observacoes = serializers.CharField(required=False, allow_blank=True)
    valor_pago = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text='Valor pago. Se não informado, usa o valor do serviço.'
    )


class AtualizarStatusAgendamentoSerializer(serializers.Serializer):
    """
    Serializer para atualizar o status de um agendamento.
    """
    status = serializers.ChoiceField(
        choices=Agendamento.Status.choices,
        required=True
    )