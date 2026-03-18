# apps/agendamentos/services.py
"""
Services para operações de agendamentos.
Este é um dos services mais complexos do sistema.
Atualizado para utilizar Service Layers Pattern, eliminando N+1 Queries.
"""
import logging
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
from typing import Optional, List, Dict

from .models import Agendamento
from apps.pets.models import Pet
from apps.servicos.models import Servico
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.agendamentos.repositories import AgendamentoRepository
from apps.agendamentos.validators import AgendamentoValidator
from apps.core.audit import AuditLogger

logger = logging.getLogger(__name__)


class AgendamentoService:
    """
    Service para operações de agendamento.
    """
    
    # Portes considerados médio/grande para duração diferenciada
    PORTES_MEDIO_GRANDE = {'MEDIO', 'GRANDE', 'GIGANTE'}
    
    @staticmethod
    def obter_duracao_servico(servico, pet=None):
        """
        Retorna a duração do serviço considerando o porte do pet.
        Se o pet for de porte médio/grande/gigante e o serviço tiver
        duracao_medio_grande definida, usa essa duração.
        """
        if (pet and 
            pet.porte in AgendamentoService.PORTES_MEDIO_GRANDE and 
            servico.duracao_medio_grande):
            return servico.duracao_medio_grande
        return servico.duracao_minutos
    
    @staticmethod
    def _get_dia_semana_bd(data) -> int:
        """
        Converte o weekday do Python (0=Segunda) para o nosso BD (0=Domingo).
        """
        return (data.weekday() + 1) % 7
        
    @staticmethod
    def horarios_disponiveis(data, servico_id, pet_id=None) -> List[Dict]:
        """
        Retorna horários disponíveis otimizados usando Repository.
        Se pet_id informado, calcula duração com base no porte do pet.
        """
        # 1. Obter serviço (1 Query)
        try:
            servico = Servico.objects.get(id=servico_id)
        except Servico.DoesNotExist:
            raise ValidationError('Serviço não encontrado.')
        
        # Determinar duração com base no porte do pet
        pet = None
        if pet_id:
            try:
                pet = Pet.objects.get(id=pet_id)
            except Pet.DoesNotExist:
                pass
        duracao = AgendamentoService.obter_duracao_servico(servico, pet)
        
        dia_semana = AgendamentoService._get_dia_semana_bd(data)
        
        # 2. Obter Equipe e Grade (1 Query via SubQuery/Prefetch)
        funcionarios_ativos = AgendamentoRepository.buscar_funcionarios_disponiveis_com_expedientes(
            servico, dia_semana
        )
        
        logger.info(f"Otimização DB - Funcionários escalados no Dia {dia_semana}: {len(funcionarios_ativos)}")
        if not funcionarios_ativos:
            return []
            
        # 3. Cachear agendamentos do dia (1 Query)
        agendamentos_cache = AgendamentoRepository.buscar_agendamentos_do_dia(data)
        
        # Obter a faixa máxima global para o dia
        min_hour = min(e.hora_inicio for f in funcionarios_ativos for e in f.expedientes_hoje)
        max_hour = max(e.hora_fim for f in funcionarios_ativos for e in f.expedientes_hoje)
        
        horarios = []
        hora_atual_time = datetime.combine(data, min_hour)
        hora_fim_time = datetime.combine(data, max_hour)
        
        # Loop In-Memory de O(1) TimeBox
        while hora_atual_time < hora_fim_time:
            data_hora_slot = timezone.make_aware(hora_atual_time)
            
            # Não retornar slots que já passaram
            if data_hora_slot <= timezone.now():
                hora_atual_time += timedelta(minutes=30)
                continue
            
            slot_livre = False
            
            # Se pet_id informado, verificar se o pet já tem agendamento neste horário
            if pet and AgendamentoRepository.verificar_conflito_pet(pet.id, data_hora_slot, duracao):
                slot_livre = False
            elif servico.tipo == Servico.TipoServico.BANHO_TOSA:
                # BANHO_TOSA precisa de TODOS os funcionários livres (tosador + atendente)
                todos_livres = True
                for func in funcionarios_ativos:
                    dentro_expediente = AgendamentoValidator.validar_horario_dentro_expediente(
                        data_hora_slot.time(), duracao, func.expedientes_hoje
                    )
                    if not dentro_expediente:
                        todos_livres = False
                        break
                    tem_conflito = AgendamentoRepository.verificar_conflito_horario(
                        func.id, data_hora_slot, duracao,
                        cache_agendamentos=agendamentos_cache
                    )
                    if tem_conflito:
                        todos_livres = False
                        break
                slot_livre = todos_livres
            else:
                for func in funcionarios_ativos:
                    # Validar In-Memory Expediente
                    dentro_expediente = AgendamentoValidator.validar_horario_dentro_expediente(
                        data_hora_slot.time(), 
                        duracao, 
                        func.expedientes_hoje
                    )
                    
                    if dentro_expediente:
                        # Validar In-Memory Agenda
                        tem_conflito = AgendamentoRepository.verificar_conflito_horario(
                            func.id, 
                            data_hora_slot, 
                            duracao, 
                            cache_agendamentos=agendamentos_cache
                        )
                        if not tem_conflito:
                            slot_livre = True
                            break
            
            # Só retorna slots que estão livres
            if slot_livre:
                horarios.append({
                    'hora': data_hora_slot.strftime('%H:%M'),
                    'data_hora': data_hora_slot.isoformat(),
                    'disponivel': True
                })
            
            hora_atual_time += timedelta(minutes=30)
            
        return horarios

    @staticmethod
    def verificar_disponibilidade(data_hora, duracao_minutos):
        # Deprecated logic now mapped deeply to Repository patterns
        return True
        
    @staticmethod
    def _alocar_funcionario(data_hora, servico, pet=None, agendamento_ignorado_id=None):
        """
        Aloca um funcionário em runtime (ex: via POST Create).
        Para BANHO_TOSA, verifica se TODOS os funcionários (tosador + atendente) estão livres.
        Para demais serviços, encontra qualquer funcionário livre.
        """
        # Converter para hora local para comparar com expedientes (armazenados em horário local)
        data_hora_local = timezone.localtime(data_hora)
        duracao = AgendamentoService.obter_duracao_servico(servico, pet)
        dia_semana_bd = AgendamentoService._get_dia_semana_bd(data_hora_local.date())
        funcionarios_aptos = AgendamentoRepository.buscar_funcionarios_disponiveis_com_expedientes(
            servico, dia_semana_bd
        )
        
        if servico.tipo == Servico.TipoServico.BANHO_TOSA:
            # Precisa de TODOS os funcionários livres (tosador + atendente)
            todos_livres = True
            primeiro_func = None
            for func in funcionarios_aptos:
                dentro_expediente = AgendamentoValidator.validar_horario_dentro_expediente(
                    data_hora_local.time(), duracao, func.expedientes_hoje
                )
                if not dentro_expediente:
                    todos_livres = False
                    break
                conflito = AgendamentoRepository.verificar_conflito_horario(
                    func.id, data_hora, duracao, agendamento_ignorado_id=agendamento_ignorado_id
                )
                if conflito:
                    todos_livres = False
                    break
                if primeiro_func is None:
                    primeiro_func = func
            return primeiro_func if todos_livres else None
        
        for func in funcionarios_aptos:
            dentro_expediente = AgendamentoValidator.validar_horario_dentro_expediente(
                data_hora_local.time(), 
                duracao, 
                func.expedientes_hoje
            )
            
            if dentro_expediente:
                conflito = AgendamentoRepository.verificar_conflito_horario(
                    func.id, data_hora, duracao, agendamento_ignorado_id=agendamento_ignorado_id
                )
                if not conflito:
                    return func
        return None
    
    @staticmethod
    @transaction.atomic
    def criar_agendamento(cliente, pet_id, servico_id, data_hora, forma_pagamento_id, observacoes=''):
        """
        Cria um novo agendamento validando negócio via Validators & Repository.
        """
        # 1. Busca instâncias base
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            raise ValidationError('Pet não encontrado.')
            
        if not pet.ativo:
            raise ValidationError('Pet inativo.')
            
        valido_pet, err_pet = AgendamentoValidator.validar_pet_pertence_cliente(pet, cliente)
        if not valido_pet:
            raise ValidationError(err_pet)
        
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
            
        # 2. Validators Customizados (Tempo Futuro já deve vir garantido pela API Serializer, 
        #    mas service previne buracos na model layer).
        valido_futuro, err_fut = AgendamentoValidator.validar_data_hora_futura(data_hora)
        if not valido_futuro:
            raise ValidationError(err_fut)
            
        # 3. Verificar conflito de horário do pet (mesmo pet não pode estar em 2 serviços)
        duracao_real = AgendamentoService.obter_duracao_servico(servico, pet)
        if AgendamentoRepository.verificar_conflito_pet(pet.id, data_hora, duracao_real):
            raise ValidationError('Este pet já possui um agendamento neste horário.')
            
        # 4. Alocação
        funcionario = AgendamentoService._alocar_funcionario(data_hora, servico, pet=pet)
        if not funcionario:
            raise ValidationError('Horário indisponível (agendamentos em conflito ou fora de expediente).')
            
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=data_hora,
            duracao_real=duracao_real,
            observacoes=observacoes,
            status=Agendamento.Status.AGENDADO
        )

        # Auditoria — rastreabilidade LGPD
        AuditLogger.log_agendamento_criado(agendamento)
        
        # Enviar SMS/Notificação Assíncrona via Celery se disponível
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_confirmacao_agendamento(agendamento)
        except ImportError:
            pass
            
        return agendamento
    
    @staticmethod
    @transaction.atomic
    def cancelar_agendamento(agendamento, motivo=''):
        """ Cancela de forma segura validando o status original. """
        if not agendamento.pode_cancelar:
            raise ValidationError('Este agendamento não pode ser cancelado (veja regras de Status).')
        
        agendamento.status = Agendamento.Status.CANCELADO
        if motivo:
            agendamento.observacoes += f'\nMotivo do cancelamento: {motivo}'
        agendamento.save()

        # Auditoria — rastreabilidade de cancelamentos
        AuditLogger.log_agendamento_cancelado(agendamento, motivo)
        
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_cancelamento_agendamento(agendamento)
        except ImportError:
            pass
            
        return agendamento
    
    @staticmethod
    @transaction.atomic
    def reagendar(agendamento, nova_data_hora, forma_pagamento_id=None, force=False):
        """ Reagenda validando tempo e forçando re-alocação segura. """
        if not force and not agendamento.pode_cancelar:
            raise ValidationError('Status não permite reagendar (deve estar Agendado ou Confirmado).')
            
        valido_futuro, err_fut = AgendamentoValidator.validar_data_hora_futura(nova_data_hora)
        if not valido_futuro:
            raise ValidationError(err_fut)
        
        # Verificar conflito de pet no novo horário (ignorando o próprio agendamento)
        pet = agendamento.pet
        servico = agendamento.servico
        duracao_real = AgendamentoService.obter_duracao_servico(servico, pet)
        if AgendamentoRepository.verificar_conflito_pet(
            pet.id, nova_data_hora, duracao_real, agendamento_ignorado_id=agendamento.id
        ):
            raise ValidationError('Este pet já possui um agendamento neste horário.')
            
        data_anterior = agendamento.data_hora
        novo_funcionario = AgendamentoService._alocar_funcionario(
            nova_data_hora, 
            servico,
            pet=pet,
            agendamento_ignorado_id=agendamento.id
        )
        if not novo_funcionario:
            raise ValidationError('Novo horário indisponível para equipe ou fora da grade funcional.')
            
        agendamento.data_hora = nova_data_hora
        agendamento.funcionario = novo_funcionario
        agendamento.duracao_real = duracao_real
        agendamento.status = Agendamento.Status.AGENDADO

        # Atualizar forma de pagamento se informada
        if forma_pagamento_id:
            from apps.pagamentos.models import FormaPagamento
            try:
                forma = FormaPagamento.objects.get(id=forma_pagamento_id)
                agendamento.forma_pagamento = forma
            except FormaPagamento.DoesNotExist:
                raise ValidationError('Forma de pagamento não encontrada.')

        agendamento.save()

        # Auditoria — rastreabilidade de reagendamentos
        AuditLogger.log_agendamento_reagendado(agendamento, data_anterior)
        
        try:
            from apps.notificacoes.services import NotificacaoService
            NotificacaoService.enviar_reagendamento(agendamento)
        except ImportError:
            pass
            
        return agendamento
    
    @staticmethod
    def iniciar_agendamento(agendamento, funcionario):
        """ Action interna dos Vets """
        if not agendamento.pode_iniciar:
            raise ValidationError('Status do Agendamento não permite inicia-lo.')
            
        agendamento.status = Agendamento.Status.EM_ANDAMENTO
        agendamento.funcionario = funcionario
        agendamento.save()
        return agendamento
    
    @staticmethod
    @transaction.atomic
    def concluir_agendamento(agendamento, observacoes='', valor_pago=None, forma_pagamento_id=None):
        if not agendamento.pode_concluir:
            raise ValidationError('Este agendamento não pode ser concluído.')

        # Atualiza forma de pagamento se informada
        if forma_pagamento_id:
            from apps.pagamentos.models import FormaPagamento
            try:
                agendamento.forma_pagamento = FormaPagamento.objects.get(id=forma_pagamento_id)
            except FormaPagamento.DoesNotExist:
                pass

        agendamento.status = Agendamento.Status.CONCLUIDO
        agendamento.status_pagamento = Agendamento.StatusPagamento.PAGO
        if valor_pago is not None:
            agendamento.valor_pago = valor_pago
        else:
            agendamento.valor_pago = agendamento.servico.preco
        if observacoes:
            agendamento.observacoes += f'\n{observacoes}'
        agendamento.save()

        # Auditoria — rastreabilidade finânceira
        AuditLogger.log_agendamento_concluido(agendamento, valor_pago)
        
        # Histórico
        try:
            from apps.historico.models import HistoricoAtendimento
            
            v_pago = valor_pago if valor_pago is not None else agendamento.servico.preco
            
            HistoricoAtendimento.objects.get_or_create(
                agendamento=agendamento,
                defaults={
                    'pet': agendamento.pet,
                    'forma_pagamento': agendamento.forma_pagamento,
                    'data_atendimento': timezone.now(),
                    'tipo_servico': agendamento.servico.tipo,
                    'observacoes': observacoes,
                    'valor_pago': v_pago
                }
            )
        except ImportError:
            pass
            
        return agendamento
