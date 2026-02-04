# apps/notificacoes/services.py
"""
Services para envio de notificações.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Notificacao


class NotificacaoService:
    """
    Service centralizado para envio de notificações.
    """
    
    @staticmethod
    def enviar_confirmacao_agendamento(agendamento):
        """
        Envia notificação de confirmação de agendamento.
        """
        cliente = agendamento.cliente
        destinatario = cliente.usuario.email
        
        assunto = f'Agendamento Confirmado - {agendamento.servico.get_tipo_display()}'
        mensagem = NotificacaoService._gerar_mensagem_confirmacao(agendamento)
        
        # Criar registro de notificação
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.CONFIRMACAO,
            canal=Notificacao.CanalNotificacao.EMAIL,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem
        )
        
        # Enviar de forma assíncrona
        try:
            from .tasks import enviar_email_async
            enviar_email_async.delay(notificacao.id)
        except ImportError:
            # Se Celery não estiver disponível, enviar síncrono
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_lembrete_agendamento(agendamento):
        """
        Envia lembrete de agendamento (24h antes).
        """
        cliente = agendamento.cliente
        destinatario = cliente.usuario.email
        
        assunto = 'Lembrete: Agendamento Amanhã'
        mensagem = NotificacaoService._gerar_mensagem_lembrete(agendamento)
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.LEMBRETE,
            canal=Notificacao.CanalNotificacao.EMAIL,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem
        )
        
        # Enviar email
        try:
            from .tasks import enviar_email_async
            enviar_email_async.delay(notificacao.id)
        except ImportError:
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_cancelamento_agendamento(agendamento):
        """
        Envia notificação de cancelamento.
        """
        cliente = agendamento.cliente
        destinatario = cliente.usuario.email
        
        assunto = 'Agendamento Cancelado'
        mensagem = NotificacaoService._gerar_mensagem_cancelamento(agendamento)
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.CANCELAMENTO,
            canal=Notificacao.CanalNotificacao.EMAIL,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem
        )
        
        try:
            from .tasks import enviar_email_async
            enviar_email_async.delay(notificacao.id)
        except ImportError:
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_reagendamento(agendamento):
        """
        Envia notificação de reagendamento.
        """
        cliente = agendamento.cliente
        destinatario = cliente.usuario.email
        
        assunto = 'Agendamento Reagendado'
        mensagem = NotificacaoService._gerar_mensagem_reagendamento(agendamento)
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.REAGENDAMENTO,
            canal=Notificacao.CanalNotificacao.EMAIL,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem
        )
        
        try:
            from .tasks import enviar_email_async
            enviar_email_async.delay(notificacao.id)
        except ImportError:
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_conclusao_servico(agendamento):
        """
        Envia notificação de conclusão de serviço.
        """
        cliente = agendamento.cliente
        destinatario = cliente.usuario.email
        
        assunto = 'Serviço Concluído'
        mensagem = NotificacaoService._gerar_mensagem_conclusao(agendamento)
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo=Notificacao.TipoNotificacao.CONCLUSAO,
            canal=Notificacao.CanalNotificacao.EMAIL,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem
        )
        
        try:
            from .tasks import enviar_email_async
            enviar_email_async.delay(notificacao.id)
        except ImportError:
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def _enviar_email_sincrono(notificacao):
        """
        Envia email de forma síncrona (fallback).
        """
        try:
            send_mail(
                subject=notificacao.assunto,
                message=notificacao.mensagem,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notificacao.destinatario],
                html_message=notificacao.mensagem,
                fail_silently=False,
            )
            notificacao.enviada = True
            notificacao.data_envio = timezone.now()
            notificacao.save()
        except Exception as e:
            notificacao.tentativas += 1
            notificacao.erro = str(e)
            notificacao.save()
    
    # Métodos privados para gerar mensagens
    @staticmethod
    def _gerar_mensagem_confirmacao(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        Seu agendamento foi confirmado!
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.get_tipo_display()}
        Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        Aguardamos você!
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_lembrete(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        Lembrete: Você tem um agendamento amanhã!
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.get_tipo_display()}
        Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        Não esqueça!
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_cancelamento(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        Seu agendamento foi cancelado.
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.get_tipo_display()}
        Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_reagendamento(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        Seu agendamento foi reagendado.
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.get_tipo_display()}
        Nova Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_conclusao(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        O serviço do seu pet foi concluído com sucesso!
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.get_tipo_display()}
        
        Obrigado pela confiança!
        FarmaVet Pet Shop
        """

