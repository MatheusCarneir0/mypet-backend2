# apps/servicos/views.py
"""
Views para gerenciamento de serviços.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Servico
from .serializers import (
    ServicoSerializer,
    ServicoListSerializer,
    ServicoCreateUpdateSerializer
)
from apps.swagger.servicos import servico_view_schema


@servico_view_schema
class ServicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Serviço.
    """
    queryset = Servico.objects.filter(ativo=True)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServicoCreateUpdateSerializer
        return ServicoSerializer
