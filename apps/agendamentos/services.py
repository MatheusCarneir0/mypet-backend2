# apps/agendamentos/services.py
"""
Services para operações de agendamentos.
Este é um dos services mais complexos do sistema.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Agendamento
from apps.pets.models import Pet
from apps.servicos.models import Servico
from apps.funcionarios.models import Funcionario


class AgendamentoService:
    """
    Service para operações de agendamento.
    """
    
    @staticmethod
    def horarios_disponiveis(data, servico_id):
        """
        Retorna horários disponíveis para um serviço em uma data.
        
        Args:
            data: Data para consulta
            servico_id: ID do serviço
        
        Returns:
            list: Lista de horários disponíveis
        """
        try:
            servico = Servico.objects.get(id=servico_id)
        except Servico.DoesNotExist:
            raise ValidationError('Serviço não encontrado.')
        
        horarios = []
        
        # Horário comercial: 8h às 18h
        hora_inicio = 8
        hora_fim = 18
        
        # Gerar slots de 30 em 30 minutos
        hora_atual = hora_inicio
        while hora_atual < hora_fim:
            data_hora = timezone.make_aware(
                datetime.combine(data, datetime.min.time().replace(hour=hora_atual))
            )
            
            # Verificar se horário está disponível
            if AgendamentoService.verificar_disponibilidade(data_hora, servico.duracao_minutos):
                horarios.append({
                    'hora': f'{hora_atual:02d}:00',
                    'data_hora': data_hora.isoformat(),
                    'disponivel': True
                })
            else:
                horarios.append({
                    'hora': f'{hora_atual:02d}:00',
                    'data_hora': data_hora.isoformat(),
                    'disponivel': False
                })
            
            hora_atual += 1
        
        return horarios
    
    @staticmethod
    def verificar_disponibilidade(data_hora, duracao_minutos):
        """
        Verifica se um horário está disponível.
        
        Args:
            data_hora: Data e hora para verificar
            duracao_minutos: Duração do serviço em minutos
        
        Returns:
            bool: True se disponível
        """
        # Calcular fim do agendamento
        fim = data_hora + timedelta(minutes=duracao_minutos)
        
        # Buscar agendamentos conflitantes
        conflitos = Agendamento.objects.filter(
            data_hora__lt=fim,
            data_hora__gte=data_hora,
            status__in=[
                Agendamento.Status.AGENDADO,
                Agendamento.Status.CONFIRMADO,
                Agendamento.Status.EM_ANDAMENTO
            ],
            ativo=True
        ).exists()
        
        return not conflitos
    
    @staticmethod
    @transaction.atomic
    def criar_agendamento(cliente, pet_id, servico_id, data_hora, forma_pagamento_id, observacoes=''):
        """
        Cria um novo agendamento.
        
        Args:
            cliente: Instância do cliente
            pet_id: ID do pet
            servico_id: ID do serviço
            data_hora: Data e hora do agendamento
            forma_pagamento_id: ID da forma de pagamento escolhida
            observacoes: Observações opcionais
        
        Returns:
            Agendamento: Instância do agendamento criado
        """
        # Validações
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            raise ValidationError('Pet não encontrado.')
        
        if pet.cliente != cliente:
            raise ValidationError('O pet não pertence a este cliente.')
        
        if not pet.ativo:
            raise ValidationError('Pet inativo.')
        
        try:
            servico = Servico.objects.get(id=servico_id)
        except Servico.DoesNotExist:
            raise ValidationError('Serviço não encontrado.')
        
        if not servico.ativo:
            raise ValidationError('Serviço inativo.')
        
        # Validar forma de pagamento
        try:
            from apps.pagamentos.models import FormaPagamento
            forma_pagamento = FormaPagamento.objects.get(id=forma_pagamento_id)
        except FormaPagamento.DoesNotExist:
            raise ValidationError('Forma de pagamento não encontrada.')
        
        if not forma_pagamento.ativo:
            raise ValidationError('Forma de pagamento inativa.')
        
        # Verificar disponibilidade
        if not AgendamentoService.verificar_disponibilidade(
            data_hora, servico.duracao_minutos
        ):
            raise ValidationError('Horário indisponível.')
        
        # Alocar funcionário disponível (lógica simplificada)
        funcionario = AgendamentoService._alocar_funcionario(data_hora, servico)
        
        # Criar agendamento
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=data_hora,
            observacoes=observacoes,
            status=Agendamento.Status.AGENDADO
        )
        
        # Enviar notificação de confirmação (se service existir)
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_confirmacao_agendamento(agendamento)
        except ImportError:
            pass  # Service ainda não implementado
        
        return agendamento
    
    @staticmethod
    def _alocar_funcionario(data_hora, servico):
        """
        Aloca um funcionário disponível para o agendamento.
        Lógica simplificada - escolhe o primeiro disponível.
        """
        # Buscar funcionários ativos
        funcionarios = Funcionario.objects.filter(ativo=True)
        
        # Para veterinário, buscar apenas veterinários
        if servico.tipo == Servico.TipoServico.VETERINARIO:
            funcionarios = funcionarios.filter(cargo=Funcionario.Cargo.VETERINARIO)
        # Para banho/tosa, buscar tosadores
        elif servico.tipo in [Servico.TipoServico.BANHO, Servico.TipoServico.TOSA, Servico.TipoServico.BANHO_TOSA]:
            funcionarios = funcionarios.filter(cargo=Funcionario.Cargo.TOSADOR)
        
        # Verificar disponibilidade de cada um
        for funcionario in funcionarios:
            conflito = Agendamento.objects.filter(
                funcionario=funcionario,
                data_hora=data_hora,
                status__in=[
                    Agendamento.Status.AGENDADO,
                    Agendamento.Status.CONFIRMADO,
                    Agendamento.Status.EM_ANDAMENTO
                ],
                ativo=True
            ).exists()
            
            if not conflito:
                return funcionario
        
        return None  # Nenhum funcionário disponível
    
    @staticmethod
    @transaction.atomic
    def cancelar_agendamento(agendamento, motivo=''):
        """
        Cancela um agendamento.
        """
        if not agendamento.pode_cancelar:
            raise ValidationError('Este agendamento não pode ser cancelado.')
        
        agendamento.status = Agendamento.Status.CANCELADO
        if motivo:
            agendamento.observacoes += f'\nMotivo do cancelamento: {motivo}'
        agendamento.save()
        
        # Enviar notificação de cancelamento
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_cancelamento_agendamento(agendamento)
        except ImportError:
            pass
        
        return agendamento
    
    @staticmethod
    @transaction.atomic
    def reagendar(agendamento, nova_data_hora):
        """
        Reagenda um agendamento.
        """
        if not agendamento.pode_cancelar:
            raise ValidationError('Este agendamento não pode ser reagendado.')
        
        # Verificar disponibilidade do novo horário
        if not AgendamentoService.verificar_disponibilidade(
            nova_data_hora, agendamento.servico.duracao_minutos
        ):
            raise ValidationError('Novo horário indisponível.')
        
        # Atualizar agendamento
        agendamento.data_hora = nova_data_hora
        agendamento.status = Agendamento.Status.AGENDADO
        agendamento.save()
        
        # Enviar notificação de reagendamento
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_reagendamento(agendamento)
        except ImportError:
            pass
        
        return agendamento
    
    @staticmethod
    def iniciar_agendamento(agendamento, funcionario):
        """
        Inicia um agendamento (muda status para EM_ANDAMENTO).
        """
        if not agendamento.pode_iniciar:
            raise ValidationError('Este agendamento não pode ser iniciado.')
        
        agendamento.status = Agendamento.Status.EM_ANDAMENTO
        agendamento.funcionario = funcionario
        agendamento.save()
        
        return agendamento
    
    @staticmethod
    @transaction.atomic
    def concluir_agendamento(agendamento, observacoes='', valor_pago=None):
        """
        Conclui um agendamento e cria registro no histórico.
        """
        if not agendamento.pode_concluir:
            raise ValidationError('Este agendamento não pode ser concluído.')
        
        # Atualizar agendamento
        agendamento.status = Agendamento.Status.CONCLUIDO
        if observacoes:
            agendamento.observacoes += f'\n{observacoes}'
        agendamento.save()
        
        # Criar registro no histórico (UC15)
        try:
            from apps.historico.models import HistoricoAtendimento
            from django.utils import timezone
            
            # Usar valor do serviço se não fornecido
            if valor_pago is None:
                valor_pago = agendamento.servico.preco
            
            HistoricoAtendimento.objects.get_or_create(
                agendamento=agendamento,
                defaults={
                    'pet': agendamento.pet,
                    'forma_pagamento': agendamento.forma_pagamento,
                    'data_atendimento': timezone.now(),
                    'tipo_servico': agendamento.servico.tipo,
                    'observacoes': observacoes,
                    'valor_pago': valor_pago
                }
            )
        except ImportError:
            pass  # Modelo ainda não existe
        
        return agendamento

