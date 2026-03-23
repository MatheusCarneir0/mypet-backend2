# apps/funcionarios/views.py
"""
Views para gerenciamento de funcionários.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Funcionario, HorarioTrabalho
from .serializers import (
    FuncionarioSerializer,
    FuncionarioCreateSerializer,
    FuncionarioUpdateSerializer,
    HorarioTrabalhoSerializer,
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
        if self.action == 'create':
            return FuncionarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FuncionarioUpdateSerializer
        return FuncionarioSerializer


from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Funcionários"])
class HorarioTrabalhoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Horário de Trabalho dos Funcionários.
    Apenas Administradores podem gerenciar.
    """
    queryset = HorarioTrabalho.objects.filter(ativo=True)
    serializer_class = HorarioTrabalhoSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]
    filterset_fields = ['funcionario', 'dia_semana']

    def perform_destroy(self, instance):
        instance.delete()  # usa o soft delete do BaseModel
