# apps/agendamentos/filters.py
"""
Filters para agendamentos.
"""
from django_filters import rest_framework as filters
from .models import Agendamento


class AgendamentoFilter(filters.FilterSet):
    """
    Filter customizado para agendamentos.
    """
    data_inicio = filters.DateFilter(field_name='data_hora', lookup_expr='gte')
    data_fim = filters.DateFilter(field_name='data_hora', lookup_expr='lte')
    status = filters.MultipleChoiceFilter(choices=Agendamento.Status.choices)
    cliente_id = filters.NumberFilter(field_name='cliente__id')
    pet_id = filters.NumberFilter(field_name='pet__id')
    servico_id = filters.NumberFilter(field_name='servico__id')
    funcionario_id = filters.NumberFilter(field_name='funcionario__id')
    
    class Meta:
        model = Agendamento
        fields = ['status', 'cliente_id', 'pet_id', 'servico_id', 'funcionario_id']

