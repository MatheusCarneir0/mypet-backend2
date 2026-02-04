# apps/notificacoes/tasks.py
"""
Tasks Celery para envio assíncrono de notificações.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notificacao
from apps.agendamentos.models import Agendamento
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def enviar_email_async(self, notificacao_id):
    """
    Envia email de forma assíncrona.
    """
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        
        # Enviar email
        send_mail(
            subject=notificacao.assunto,
            message=notificacao.mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notificacao.destinatario],
            html_message=notificacao.mensagem,
            fail_silently=False,
        )
        
        # Atualizar notificação
        notificacao.enviada = True
        notificacao.data_envio = timezone.now()
        notificacao.save()
        
        logger.info(f'Email enviado com sucesso: {notificacao_id}')
        
    except Exception as exc:
        try:
            notificacao = Notificacao.objects.get(id=notificacao_id)
            notificacao.tentativas += 1
            notificacao.erro = str(exc)
            notificacao.save()
        except:
            pass
        
        logger.error(f'Erro ao enviar email {notificacao_id}: {exc}')
        
        # Retry com delay exponencial
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def enviar_lembretes_agendamentos():
    """
    Task periódica para enviar lembretes de agendamentos.
    Executa diariamente às 8h.
    """
    # Buscar agendamentos para amanhã
    amanha = timezone.now() + timedelta(days=1)
    inicio = amanha.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = amanha.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    agendamentos = Agendamento.objects.filter(
        data_hora__range=[inicio, fim],
        status__in=[
            Agendamento.Status.AGENDADO,
            Agendamento.Status.CONFIRMADO
        ],
        ativo=True
    )
    
    from .services import NotificacaoService
    
    for agendamento in agendamentos:
        # Verificar se já enviou lembrete
        lembrete_existente = Notificacao.objects.filter(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.LEMBRETE,
            enviada=True
        ).exists()
        
        if not lembrete_existente:
            NotificacaoService.enviar_lembrete_agendamento(agendamento)
    
    logger.info(f'Lembretes enviados: {agendamentos.count()}')

