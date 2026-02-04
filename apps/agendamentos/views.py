# apps/agendamentos/views.py
"""
Views para gerenciamento de agendamentos.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from .models import Agendamento
from .serializers import (
    AgendamentoSerializer,
    AgendamentoListSerializer,
    AgendamentoCreateSerializer,
    AgendamentoDetailSerializer,
    ConcluirAgendamentoSerializer,
)
from .services import AgendamentoService
from .filters import AgendamentoFilter
from apps.swagger.agendamentos import agendamento_view_schema


@agendamento_view_schema
class AgendamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações de Agendamento.
    SEGURANÇA CRÍTICA: Bloqueia métodos PUT, PATCH e DELETE genéricos.
    As alterações de estado devem ser Ações de Negócio (POST).
    """
    queryset = Agendamento.objects.all().select_related(
        'cliente', 'pet', 'servico', 'funcionario'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AgendamentoFilter
    ordering_fields = ['data_hora', 'status']
    ordering = ['-data_hora']
    # Bloquear PUT, PATCH e DELETE - apenas GET e POST permitidos
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_serializer_class(self):
        """
        Serializers por ação.
        """
        if self.action == 'list':
            return AgendamentoListSerializer
        elif self.action == 'create':
            return AgendamentoCreateSerializer
        elif self.action == 'retrieve':
            return AgendamentoDetailSerializer
        return AgendamentoSerializer
    
    def get_permissions(self):
        """
        Permissões por ação.
        """
        if self.action in ['cancelar', 'reagendar']:
            # Cliente pode cancelar/reagendar seus próprios agendamentos
            from apps.core.permissions import IsOwnerOrAdmin
            return [IsOwnerOrAdmin()]
        elif self.action in ['iniciar', 'concluir']:
            # Apenas funcionário pode iniciar/concluir
            from apps.core.permissions import IsFuncionario
            return [IsFuncionario()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """
        Filtrar agendamentos baseado no tipo de usuário.
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Cliente vê apenas seus agendamentos
        if user.is_cliente:
            try:
                return queryset.filter(cliente__usuario=user)
            except:
                return queryset.none()
        
        # Funcionário vê agendamentos atribuídos a ele
        elif user.is_funcionario:
            try:
                return queryset.filter(funcionario__usuario=user)
            except:
                return queryset.none()
        
        # Administrador vê todos
        return queryset
    
    def perform_create(self, serializer):
        """
        Criar agendamento via service.
        """
        try:
            cliente = self.request.user.cliente
            agendamento = AgendamentoService.criar_agendamento(
                cliente=cliente,
                pet_id=serializer.validated_data['pet'].id,
                servico_id=serializer.validated_data['servico'].id,
                data_hora=serializer.validated_data['data_hora'],
                forma_pagamento_id=serializer.validated_data['forma_pagamento'].id,
                observacoes=serializer.validated_data.get('observacoes', '')
            )
            # Atribuir o agendamento criado ao serializer para retornar
            serializer.instance = agendamento
        except Exception as e:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError({'error': str(e)})
    
    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """
        POST /agendamentos/{id}/cancelar/
        Cancela um agendamento. Exigir motivo no corpo (UC07).
        """
        agendamento = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if not motivo:
            return Response({
                'error': 'Campo "motivo" é obrigatório para cancelamento.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            AgendamentoService.cancelar_agendamento(agendamento, motivo)
            return Response({
                'message': 'Agendamento cancelado com sucesso.',
                'agendamento': AgendamentoDetailSerializer(agendamento).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='reagendar')
    def reagendar(self, request, pk=None):
        """
        POST /agendamentos/{id}/reagendar/
        Reagenda um agendamento. Validar nova data_hora via AgendamentoService (UC08).
        """
        agendamento = self.get_object()
        nova_data_hora = request.data.get('data_hora')
        
        if not nova_data_hora:
            return Response({
                'error': 'Campo "data_hora" é obrigatório.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            if isinstance(nova_data_hora, str):
                nova_data_hora = timezone.datetime.fromisoformat(nova_data_hora.replace('Z', '+00:00'))
            
            AgendamentoService.reagendar(agendamento, nova_data_hora)
            return Response({
                'message': 'Agendamento reagendado com sucesso.',
                'agendamento': AgendamentoDetailSerializer(agendamento).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='iniciar')
    def iniciar(self, request, pk=None):
        """
        POST /agendamentos/{id}/iniciar/
        Inicia um agendamento. Alterar status para EM_ANDAMENTO (Apenas funcionário).
        """
        agendamento = self.get_object()
        
        try:
            funcionario = request.user.funcionario
            AgendamentoService.iniciar_agendamento(agendamento, funcionario)
            return Response({
                'message': 'Agendamento iniciado.',
                'agendamento': AgendamentoDetailSerializer(agendamento).data
            }, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({
                'error': 'Apenas funcionários podem iniciar agendamentos.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='concluir')
    def concluir(self, request, pk=None):
        """
        POST /agendamentos/{id}/concluir/
        Finaliza serviço, captura observacoes, registra pagamento e 
        gera entrada no HistoricoAtendimento (UC15).
        """
        agendamento = self.get_object()
        serializer = ConcluirAgendamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            valor_pago = serializer.validated_data.get('valor_pago')
            observacoes = serializer.validated_data.get('observacoes', '')
            
            AgendamentoService.concluir_agendamento(
                agendamento,
                observacoes=observacoes,
                valor_pago=valor_pago
            )
            return Response({
                'message': 'Agendamento concluído. Histórico registrado.',
                'agendamento': AgendamentoDetailSerializer(agendamento).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='disponibilidade')
    def disponibilidade(self, request):
        """
        GET /agendamentos/disponibilidade/
        Query params: data e servico_id para retornar horários livres (UC06).
        """
        data_str = request.query_params.get('data')
        servico_id = request.query_params.get('servico_id')
        
        if not data_str or not servico_id:
            return Response({
                'error': 'Parâmetros "data" e "servico_id" são obrigatórios.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            horarios = AgendamentoService.horarios_disponiveis(data_obj, int(servico_id))
            return Response({
                'data': data_str,
                'servico_id': int(servico_id),
                'horarios': horarios
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({
                'error': f'Formato de data inválido. Use YYYY-MM-DD. Erro: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
