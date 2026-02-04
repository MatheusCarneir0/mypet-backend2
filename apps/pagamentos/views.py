# apps/pagamentos/views.py
"""
Views para gerenciamento de pagamentos.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FormaPagamento, TransacaoPagamento
from .serializers import (
    FormaPagamentoSerializer,
    TransacaoPagamentoSerializer,
    ProcessarPagamentoDinheiroSerializer,
    ProcessarPagamentoCartaoSerializer,
    ProcessarPagamentoPixSerializer,
    ConfirmarPagamentoPixSerializer
)
from .services import PagamentoService
from apps.agendamentos.models import Agendamento
from apps.swagger.pagamentos import (
    forma_pagamento_view_schema,
    transacao_pagamento_view_schema
)


@forma_pagamento_view_schema
class FormaPagamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para formas de pagamento (somente leitura).
    """
    queryset = FormaPagamento.objects.filter(ativo=True)
    serializer_class = FormaPagamentoSerializer
    permission_classes = [IsAuthenticated]


@transacao_pagamento_view_schema
class TransacaoPagamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para transações de pagamento.
    """
    queryset = TransacaoPagamento.objects.all().select_related(
        'agendamento', 'forma_pagamento'
    )
    serializer_class = TransacaoPagamentoSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='processar-dinheiro')
    def processar_dinheiro(self, request):
        """
        Processa pagamento em dinheiro.
        """
        serializer = ProcessarPagamentoDinheiroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            agendamento = Agendamento.objects.get(
                id=serializer.validated_data['agendamento_id']
            )
            
            transacao = PagamentoService.processar_pagamento_dinheiro(
                agendamento=agendamento,
                valor_recebido=serializer.validated_data['valor_recebido'],
                observacoes=serializer.validated_data.get('observacoes', '')
            )
            
            return Response(
                TransacaoPagamentoSerializer(transacao).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='processar-cartao')
    def processar_cartao(self, request):
        """
        Processa pagamento com cartão.
        """
        serializer = ProcessarPagamentoCartaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            agendamento = Agendamento.objects.get(
                id=serializer.validated_data['agendamento_id']
            )
            
            transacao = PagamentoService.processar_pagamento_cartao(
                agendamento=agendamento,
                forma_pagamento_id=serializer.validated_data['forma_pagamento_id'],
                numero_transacao=serializer.validated_data['numero_transacao'],
                bandeira_cartao=serializer.validated_data['bandeira_cartao'],
                ultimos_digitos=serializer.validated_data['ultimos_digitos'],
                observacoes=serializer.validated_data.get('observacoes', '')
            )
            
            return Response(
                TransacaoPagamentoSerializer(transacao).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='gerar-pix')
    def gerar_pix(self, request):
        """
        Gera QR Code e código PIX para pagamento.
        """
        serializer = ProcessarPagamentoPixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            agendamento = Agendamento.objects.get(
                id=serializer.validated_data['agendamento_id']
            )
            
            transacao = PagamentoService.gerar_pagamento_pix(
                agendamento=agendamento,
                observacoes=serializer.validated_data.get('observacoes', '')
            )
            
            return Response(
                TransacaoPagamentoSerializer(transacao).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='confirmar-pix')
    def confirmar_pix(self, request):
        """
        Confirma recebimento de pagamento PIX.
        """
        serializer = ConfirmarPagamentoPixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            transacao = PagamentoService.confirmar_pagamento_pix(
                transacao_id=serializer.validated_data['transacao_id'],
                pix_txid=serializer.validated_data.get('pix_txid')
            )
            
            return Response(
                TransacaoPagamentoSerializer(transacao).data
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
