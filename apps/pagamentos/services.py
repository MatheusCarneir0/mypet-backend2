# apps/pagamentos/services.py
"""
Services para operações de pagamento LOCAL (sem gateway).
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from .models import FormaPagamento, TransacaoPagamento
from apps.historico.models import HistoricoAtendimento


class PagamentoService:
    """
    Service para operações de pagamento LOCAL.
    Sistema de cidade pequena - sem gateway.
    """
    
    @staticmethod
    @transaction.atomic
    def processar_pagamento_dinheiro(agendamento, valor_recebido, observacoes=''):
        """
        Processa pagamento em dinheiro.
        Calcula troco automaticamente.
        
        Args:
            agendamento: Instância do agendamento
            valor_recebido: Valor em dinheiro recebido
            observacoes: Observações opcionais
        
        Returns:
            TransacaoPagamento: Transação criada
        """
        # Obter forma de pagamento "Dinheiro"
        try:
            forma_pagamento = FormaPagamento.objects.get(
                tipo=FormaPagamento.TipoPagamento.DINHEIRO
            )
        except FormaPagamento.DoesNotExist:
            raise ValidationError('Forma de pagamento Dinheiro não encontrada.')
        
        valor = agendamento.servico.preco
        
        # Validar valor recebido
        if Decimal(str(valor_recebido)) < valor:
            raise ValidationError('Valor recebido insuficiente.')
        
        # Calcular troco
        troco = Decimal(str(valor_recebido)) - valor
        
        # Criar transação
        transacao = TransacaoPagamento.objects.create(
            agendamento=agendamento,
            forma_pagamento=forma_pagamento,
            valor=valor,
            valor_recebido=valor_recebido,
            troco=troco,
            status=TransacaoPagamento.StatusPagamento.CONFIRMADO,
            data_pagamento=timezone.now(),
            observacoes=observacoes
        )
        
        # Criar histórico de atendimento
        PagamentoService._criar_historico_atendimento(agendamento, forma_pagamento, valor)
        
        # Enviar notificação de conclusão
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_conclusao_servico(agendamento)
        except ImportError:
            pass
        
        return transacao
    
    @staticmethod
    @transaction.atomic
    def processar_pagamento_cartao(
        agendamento, forma_pagamento_id, numero_transacao,
        bandeira_cartao, ultimos_digitos, observacoes=''
    ):
        """
        Processa pagamento com cartão.
        Funcionário passa na maquininha e registra dados.
        """
        try:
            forma_pagamento = FormaPagamento.objects.get(id=forma_pagamento_id)
        except FormaPagamento.DoesNotExist:
            raise ValidationError('Forma de pagamento não encontrada.')
        
        valor = agendamento.servico.preco
        
        # Criar transação
        transacao = TransacaoPagamento.objects.create(
            agendamento=agendamento,
            forma_pagamento=forma_pagamento,
            valor=valor,
            numero_transacao=numero_transacao,
            bandeira_cartao=bandeira_cartao,
            ultimos_digitos=ultimos_digitos,
            status=TransacaoPagamento.StatusPagamento.CONFIRMADO,
            data_pagamento=timezone.now(),
            observacoes=observacoes
        )
        
        # Criar histórico de atendimento
        PagamentoService._criar_historico_atendimento(agendamento, forma_pagamento, valor)
        
        # Enviar notificação de conclusão
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_conclusao_servico(agendamento)
        except ImportError:
            pass
        
        return transacao
    
    @staticmethod
    @transaction.atomic
    def gerar_pagamento_pix(agendamento, observacoes=''):
        """
        Gera QR Code e código PIX para pagamento.
        Sistema LOCAL - gera código estático.
        """
        # Obter forma de pagamento PIX
        try:
            forma_pagamento = FormaPagamento.objects.get(
                tipo=FormaPagamento.TipoPagamento.PIX
            )
        except FormaPagamento.DoesNotExist:
            raise ValidationError('Forma de pagamento PIX não encontrada.')
        
        valor = agendamento.servico.preco
        
        # Gerar Transaction ID único
        txid = str(uuid.uuid4()).replace('-', '')[:35]  # Máximo 35 caracteres
        
        # Gerar código PIX Copia e Cola
        pix_codigo = PagamentoService._gerar_codigo_pix(valor, txid)
        
        # Criar transação
        transacao = TransacaoPagamento.objects.create(
            agendamento=agendamento,
            forma_pagamento=forma_pagamento,
            valor=valor,
            pix_codigo=pix_codigo,
            pix_txid=txid,
            status=TransacaoPagamento.StatusPagamento.PENDENTE,
            observacoes=observacoes
        )
        
        # Gerar QR Code
        qr_code_file = PagamentoService._gerar_qr_code(pix_codigo, txid)
        transacao.pix_qrcode.save(f'pix_{txid}.png', qr_code_file, save=True)
        
        return transacao
    
    @staticmethod
    @transaction.atomic
    def confirmar_pagamento_pix(transacao_id, pix_txid=None):
        """
        Confirma pagamento PIX.
        Funcionário confirma manualmente que recebeu o PIX.
        """
        try:
            transacao = TransacaoPagamento.objects.get(id=transacao_id)
        except TransacaoPagamento.DoesNotExist:
            raise ValidationError('Transação não encontrada.')
        
        if transacao.status != TransacaoPagamento.StatusPagamento.PENDENTE:
            raise ValidationError('Esta transação já foi processada.')
        
        # Atualizar transação
        transacao.status = TransacaoPagamento.StatusPagamento.CONFIRMADO
        transacao.data_pagamento = timezone.now()
        if pix_txid:
            transacao.pix_txid = pix_txid
        transacao.save()
        
        # Criar histórico de atendimento
        PagamentoService._criar_historico_atendimento(
            transacao.agendamento,
            transacao.forma_pagamento,
            transacao.valor
        )
        
        # Enviar notificação de conclusão
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_conclusao_servico(transacao.agendamento)
        except ImportError:
            pass
        
        return transacao
    
    @staticmethod
    def _gerar_codigo_pix(valor, txid):
        """
        Gera código PIX Copia e Cola (formato simplificado).
        Em produção, usar biblioteca brcode ou similar.
        """
        # Formato simplificado para exemplo
        # Em produção, usar biblioteca específica para gerar BRCode válido
        chave_pix = getattr(settings, 'PIX_CHAVE', 'suachave@email.com')
        merchant_name = getattr(settings, 'PIX_MERCHANT_NAME', 'FarmaVet Pet Shop')
        merchant_city = getattr(settings, 'PIX_MERCHANT_CITY', 'Boa Viagem')
        
        # Formato simplificado (não é um BRCode válido completo)
        codigo = f'{chave_pix}|{merchant_name}|{merchant_city}|{valor}|{txid}'
        
        return codigo
    
    @staticmethod
    def _gerar_qr_code(conteudo, filename):
        """
        Gera imagem QR Code a partir de um conteúdo.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(conteudo)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salvar em BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return ContentFile(buffer.read(), name=f'{filename}.png')
    
    @staticmethod
    def _criar_historico_atendimento(agendamento, forma_pagamento, valor_pago):
        """
        Cria registro no histórico de atendimento.
        """
        HistoricoAtendimento.objects.get_or_create(
            agendamento=agendamento,
            defaults={
                'pet': agendamento.pet,
                'forma_pagamento': forma_pagamento,
                'data_atendimento': timezone.now(),
                'tipo_servico': agendamento.servico.get_tipo_display(),
                'observacoes': agendamento.observacoes,
                'valor_pago': valor_pago
            }
        )

