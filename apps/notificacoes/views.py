# apps/notificacoes/views.py
"""
Views para gerenciamento de notificações.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notificacao
from .serializers import NotificacaoSerializer, NotificacaoListSerializer
from apps.swagger.notificacoes import notificacao_view_schema


@notificacao_view_schema
class NotificacaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para notificações.
    GET /notificacoes/ - Listar notificações do usuário
    PATCH /notificacoes/{id}/read/ - Marcar como lida
    """
    queryset = Notificacao.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificacaoListSerializer
        return NotificacaoSerializer
    
    def get_queryset(self):
        """
        Filtrar notificações baseado no tipo de usuário.
        Cliente vê apenas notificações de seus agendamentos.
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Cliente vê apenas notificações de seus agendamentos
        if user.is_cliente:
            try:
                return queryset.filter(agendamento__cliente__usuario=user).order_by('-data_criacao')
            except:
                return queryset.none()
        
        # Administrador e funcionário vêem todas
        return queryset.order_by('-data_criacao')
    
    @action(detail=True, methods=['patch'], url_path='read')
    def read(self, request, pk=None):
        """
        PATCH /notificacoes/{id}/read/
        Marca uma notificação como lida.
        """
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        
        return Response({
            'message': 'Notificação marcada como lida.',
            'notificacao': NotificacaoSerializer(notificacao).data
        }, status=status.HTTP_200_OK)
