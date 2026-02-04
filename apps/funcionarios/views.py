# apps/funcionarios/views.py
"""
Views para gerenciamento de funcionários.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Funcionario
from .serializers import (
    FuncionarioSerializer,
    FuncionarioListSerializer,
    FuncionarioCreateSerializer,
    FuncionarioUpdateSerializer
)
from apps.core.permissions import IsAdministrador
from apps.swagger.funcionarios import funcionario_view_schema


@funcionario_view_schema
class FuncionarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Funcionário.
    """
    queryset = Funcionario.objects.filter(ativo=True).select_related('usuario')
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FuncionarioListSerializer
        elif self.action == 'create':
            return FuncionarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FuncionarioUpdateSerializer
        return FuncionarioSerializer
