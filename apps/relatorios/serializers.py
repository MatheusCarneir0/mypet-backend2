# apps/relatorios/serializers.py
"""
Serializers para o app de relatórios.
"""
from rest_framework import serializers
from .models import Relatorio


class RelatorioSerializer(serializers.ModelSerializer):
    """
    Serializer de Relatório.
    """
    administrador_nome = serializers.CharField(
        source='administrador.nome',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )
    formato_display = serializers.CharField(
        source='get_formato_display',
        read_only=True
    )
    
    class Meta:
        model = Relatorio
        fields = [
            'id', 'administrador', 'administrador_nome',
            'tipo', 'tipo_display', 'formato', 'formato_display',
            'data_geracao', 'filtros', 'arquivo'
        ]
        read_only_fields = ['id', 'administrador', 'data_geracao', 'arquivo']


class RelatorioCreateSerializer(serializers.Serializer):
    """
    Serializer para solicitação de geração de relatório.
    """
    tipo = serializers.ChoiceField(choices=Relatorio.TipoRelatorio.choices)
    formato = serializers.ChoiceField(choices=Relatorio.FormatoRelatorio.choices)
    data_inicio = serializers.DateField(required=False)
    data_fim = serializers.DateField(required=False)
    cliente_id = serializers.IntegerField(required=False)
    funcionario_id = serializers.IntegerField(required=False)
    servico_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        """
        Validar que as datas fazem sentido.
        """
        data_inicio = attrs.get('data_inicio')
        data_fim = attrs.get('data_fim')
        
        if data_inicio and data_fim:
            if data_inicio > data_fim:
                raise serializers.ValidationError({
                    'data_inicio': 'Data inicial não pode ser maior que data final.'
                })
        
        return attrs
