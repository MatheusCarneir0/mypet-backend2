# apps/notificacoes/services.py
"""
Services para envio de notificações.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Notificacao
import logging

logger = logging.getLogger(__name__)


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
        
        assunto = f'Agendamento Confirmado - {agendamento.servico.nome}'
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
        except Exception as e:
            # Se Celery não estiver disponível, enviar síncrono
            logger.warning(f"Celery/Redis indisponível. Fallback síncrono. Erro: {e}")
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
        except Exception as e:
            logger.warning(f"Celery/Redis indisponível. Fallback síncrono. Erro: {e}")
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
        except Exception as e:
            logger.warning(f"Celery/Redis indisponível. Fallback síncrono. Erro: {e}")
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
        except Exception as e:
            logger.warning(f"Celery/Redis indisponível. Fallback síncrono. Erro: {e}")
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
        except Exception as e:
            logger.warning(f"Celery/Redis indisponível. Fallback síncrono. Erro: {e}")
            NotificacaoService._enviar_email_sincrono(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_recuperacao_senha(usuario, reset_link):
        """
        Envia email com link para redefinição de senha.
        """
        destinatario = usuario.email
        assunto = 'MyPet — Recuperação de Senha'
        
        mensagem = f"""
        Olá, {usuario.nome}!
        
        Recebemos uma solicitação para redefinir a senha da sua conta no MyPet.
        Clique no link abaixo para escolher uma nova senha:
        
        {reset_link}
        
        Este link é válido por 24 horas.
        Se você não solicitou a alteração, pode ignorar este e-mail com segurança.
        
        FarmaVet Pet Shop
        """
        
        # Enviar email diretamente (sem registro em Notificacao model para manter simples)
        try:
            send_mail(
                subject=assunto,
                message=mensagem,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinatario],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Logar erro se necessário
            return False

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
        Serviço: {agendamento.servico.nome}
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
        Serviço: {agendamento.servico.nome}
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
        Serviço: {agendamento.servico.nome}
        Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_reagendamento(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        Seu agendamento foi reagendado.
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.nome}
        Nova Data/Hora: {agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')}
        
        FarmaVet Pet Shop
        """
    
    @staticmethod
    def _gerar_mensagem_conclusao(agendamento):
        return f"""
        Olá {agendamento.cliente.usuario.nome},
        
        O serviço do seu pet foi concluído com sucesso!
        
        Pet: {agendamento.pet.nome}
        Serviço: {agendamento.servico.nome}
        
        Obrigado pela confiança!
        FarmaVet Pet Shop
        """

