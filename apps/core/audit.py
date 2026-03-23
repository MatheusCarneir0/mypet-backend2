# apps/core/audit.py
"""
Módulo de auditoria de ações sensíveis do sistema MyPet.
Registra ações críticas para rastreabilidade (compliance LGPD e investigação de fraudes).
Usa o logger 'auditoria' configurado no settings, que grava em logs/auditoria.log.
"""
import logging
from django.utils import timezone

logger = logging.getLogger('auditoria')


def _get_ip(request):
    """Extrai o IP real do cliente, respeitando proxies reversos."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'desconhecido')


class AuditLogger:
    """
    Centralizador de logs de auditoria para ações sensíveis.
    Todos os métodos são estáticos para facilitar uso em qualquer camada.
    """

    @staticmethod
    def log_agendamento_criado(agendamento, request=None):
        """Registra criação de agendamento."""
        ip = _get_ip(request) if request else 'sistema'
        logger.info(
            f"AGENDAMENTO_CRIADO | "
            f"id={agendamento.id} | "
            f"cliente_id={agendamento.cliente.id} | "
            f"pet_id={agendamento.pet.id} | "
            f"servico={agendamento.servico.nome} | "
            f"data_hora={agendamento.data_hora} | "
            f"funcionario_id={agendamento.funcionario.id if agendamento.funcionario else 'N/A'} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_agendamento_cancelado(agendamento, motivo='', request=None):
        """Registra cancelamento de agendamento."""
        ip = _get_ip(request) if request else 'sistema'
        logger.info(
            f"AGENDAMENTO_CANCELADO | "
            f"id={agendamento.id} | "
            f"cliente_id={agendamento.cliente.id} | "
            f"motivo={motivo[:100] if motivo else 'N/A'} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_agendamento_reagendado(agendamento, data_anterior, request=None):
        """Registra reagendamento de agendamento."""
        ip = _get_ip(request) if request else 'sistema'
        logger.info(
            f"AGENDAMENTO_REAGENDADO | "
            f"id={agendamento.id} | "
            f"cliente_id={agendamento.cliente.id} | "
            f"data_anterior={data_anterior} | "
            f"nova_data={agendamento.data_hora} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_login_sucesso(usuario, request=None):
        """Registra login bem-sucedido."""
        ip = _get_ip(request) if request else 'N/A'
        logger.info(
            f"LOGIN_SUCESSO | "
            f"usuario_id={usuario.id} | "
            f"email={usuario.email} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_login_falhou(email, request=None):
        """Registra tentativa de login com falha."""
        ip = _get_ip(request) if request else 'N/A'
        logger.warning(
            f"LOGIN_FALHOU | "
            f"email={email} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_acesso_negado(usuario, recurso, request=None):
        """Registra tentativa de acesso não autorizado."""
        ip = _get_ip(request) if request else 'N/A'
        usuario_id = usuario.id if usuario and usuario.is_authenticated else 'anonimo'
        logger.warning(
            f"ACESSO_NEGADO | "
            f"usuario_id={usuario_id} | "
            f"recurso={recurso} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_registro_usuario(usuario, request=None):
        """Registra cadastro de novo usuário."""
        ip = _get_ip(request) if request else 'N/A'
        logger.info(
            f"USUARIO_CADASTRADO | "
            f"usuario_id={usuario.id} | "
            f"email={usuario.email} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )

    @staticmethod
    def log_agendamento_concluido(agendamento, valor_pago=None, request=None):
        """Registra conclusão de agendamento."""
        ip = _get_ip(request) if request else 'sistema'
        logger.info(
            f"AGENDAMENTO_CONCLUIDO | "
            f"id={agendamento.id} | "
            f"cliente_id={agendamento.cliente.id} | "
            f"servico={agendamento.servico.nome} | "
            f"valor_pago={valor_pago} | "
            f"ip={ip} | "
            f"timestamp={timezone.now().isoformat()}"
        )
