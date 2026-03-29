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
from apps.core.permissions import IsAdministrador
from apps.swagger.servicos import servico_view_schema
from drf_spectacular.utils import extend_schema, extend_schema_view


@servico_view_schema
class ServicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Serviço.
    - list/retrieve: qualquer usuário autenticado
    - create/update/delete: apenas administrador
    """
    queryset = Servico.objects.filter(ativo=True).prefetch_related('cargos')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdministrador()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServicoCreateUpdateSerializer
        return ServicoSerializer
