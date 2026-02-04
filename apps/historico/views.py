# apps/historico/views.py
"""
Views para gerenciamento de histórico de atendimentos.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import HistoricoAtendimento
from .serializers import (
    HistoricoAtendimentoSerializer,
    HistoricoAtendimentoListSerializer
)
from apps.swagger.historico import historico_view_schema


@historico_view_schema
class HistoricoAtendimentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para histórico de atendimentos (somente leitura).
    """
    queryset = HistoricoAtendimento.objects.all().select_related('pet', 'forma_pagamento')
    serializer_class = HistoricoAtendimentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['data_atendimento', 'valor_pago']
    ordering = ['-data_atendimento']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HistoricoAtendimentoListSerializer
        return HistoricoAtendimentoSerializer
    
    def get_queryset(self):
        """
        Filtrar histórico baseado no tipo de usuário.
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Cliente vê apenas histórico de seus pets
        if user.is_cliente:
            try:
                return queryset.filter(pet__cliente__usuario=user)
            except:
                return queryset.none()
        
        # Administrador e funcionário vêem todos
        return queryset
