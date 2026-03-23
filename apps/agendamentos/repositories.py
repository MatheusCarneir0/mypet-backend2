# apps/agendamentos/repositories.py
from django.db.models import Prefetch, Q
from django.utils import timezone
from datetime import datetime, time, timedelta
from apps.agendamentos.models import Agendamento
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.servicos.models import Servico

class AgendamentoRepository:
    """
    Repository pattern para abstrair consultas complexas e pesadas de Agendamentos,
    garantindo uso de select_related, prefetch_related e otimizando performance.
    """
    
    @staticmethod
    def buscar_agendamentos_do_dia(data) -> dict:
        """
        Busca TODOS os agendamentos de um dia específico em uma única query.
        Retorna um dicionário indexado pelo ID do funcionário para validação O(1) in-memory.
        """
        inicio_dia = timezone.make_aware(datetime.combine(data, time.min))
        fim_dia = timezone.make_aware(datetime.combine(data, time.max))
        
        agendamentos = Agendamento.objects.filter(
            data_hora__gte=inicio_dia,
            data_hora__lt=fim_dia,
            status__in=[
                Agendamento.Status.AGENDADO,
                Agendamento.Status.CONFIRMADO,
                Agendamento.Status.EM_ANDAMENTO
            ]
        ).select_related('funcionario', 'servico')
        
        resultado = {}
        for ag in agendamentos:
            if ag.funcionario_id:
                if ag.funcionario_id not in resultado:
                    resultado[ag.funcionario_id] = []
                resultado[ag.funcionario_id].append(ag)
                
        return resultado
        
    @staticmethod
    def buscar_funcionarios_disponiveis_com_expedientes(servico, dia_semana_bd: int):
        """
        Busca em 1 query todos os funcionários capacitados para o serviço já embutindo
        o expediente válido daquele dia da semana via Prefetch.
        Os cargos aptos são obtidos diretamente do relacionamento ServicoCargo do serviço.
        """
        from apps.servicos.models import ServicoCargo

        # Obter os cargos vinculados a este serviço
        cargos_aptos = list(
            ServicoCargo.objects.filter(servico=servico).values_list('cargo', flat=True)
        )

        funcionarios_qs = Funcionario.objects.filter(ativo=True)
        if cargos_aptos:
            funcionarios_qs = funcionarios_qs.filter(cargo__in=cargos_aptos)

        # Fazer prefetch APENAS dos horários do dia desejado
        expedientes_prefetch = Prefetch(
            'horarios_trabalho',
            queryset=HorarioTrabalho.objects.filter(dia_semana=dia_semana_bd),
            to_attr='expedientes_hoje'
        )

        # Obter a lista final que tem expedientes_hoje populado em uma segunda query de in-list
        funcionarios = list(funcionarios_qs.prefetch_related(expedientes_prefetch))

        # Manter apenas quem de fato trabalha no dia (tem item na lista expedientes_hoje)
        return [f for f in funcionarios if getattr(f, 'expedientes_hoje', [])]

    @staticmethod
    def verificar_conflito_pet(pet_id, inicio_desejado, duracao_minutos, agendamento_ignorado_id=None):
        """
        Verifica se o PET já possui agendamento ativo em horário sobreposto.
        Um mesmo pet não pode estar em dois serviços ao mesmo tempo.
        Retorna True caso HAJA conflito.
        """
        fim_desejado = inicio_desejado + timedelta(minutes=duracao_minutos)
        
        qs = Agendamento.objects.filter(
            pet_id=pet_id,
            status__in=[
                Agendamento.Status.AGENDADO,
                Agendamento.Status.CONFIRMADO,
                Agendamento.Status.EM_ANDAMENTO
            ],
            data_hora__lt=fim_desejado
        ).select_related('servico')
        if agendamento_ignorado_id:
            qs = qs.exclude(id=agendamento_ignorado_id)
            
        for ag in qs:
            ag_duracao = ag.duracao_real or ag.servico.duracao_minutos
            ag_fim = ag.data_hora + timedelta(minutes=ag_duracao)
            if ag.data_hora < fim_desejado and ag_fim > inicio_desejado:
                return True
        return False

    @staticmethod
    def verificar_conflito_cliente(cliente_id, inicio_desejado, duracao_minutos, agendamento_ignorado_id=None):
        """
        Verifica se o CLIENTE já possui qualquer agendamento ativo em horário sobreposto.
        Um cliente não pode agendar dois pets no mesmo horário.
        Retorna True caso HAJA conflito.
        """
        fim_desejado = inicio_desejado + timedelta(minutes=duracao_minutos)
        
        qs = Agendamento.objects.filter(
            cliente_id=cliente_id,
            status__in=[
                Agendamento.Status.AGENDADO,
                Agendamento.Status.CONFIRMADO,
                Agendamento.Status.EM_ANDAMENTO
            ],
            data_hora__lt=fim_desejado
        ).select_related('servico')
        if agendamento_ignorado_id:
            qs = qs.exclude(id=agendamento_ignorado_id)
            
        for ag in qs:
            ag_duracao = ag.duracao_real or ag.servico.duracao_minutos
            ag_fim = ag.data_hora + timedelta(minutes=ag_duracao)
            if ag.data_hora < fim_desejado and ag_fim > inicio_desejado:
                return True
        return False

    @staticmethod
    def verificar_conflito_horario(funcionario_id, inicio_desejado, duracao_minutos, cache_agendamentos=None, agendamento_ignorado_id=None):
        """
        Verifica se há conflito de horário.
        Se cache_agendamentos for passado (ideal), usa em memória (O(n)).
        Senão, bate no banco.
        Retorna True caso HAJA conflito, ou False caso esteja livre.
        """
        fim_desejado = inicio_desejado + timedelta(minutes=duracao_minutos)
        
        if cache_agendamentos is not None:
            # Busca O(1) in-memory
            agends_func = cache_agendamentos.get(funcionario_id, [])
            for ag in agends_func:
                if agendamento_ignorado_id and ag.id == agendamento_ignorado_id:
                    continue
                # Overlap test: (InicioA < FimB) e (FimA > InicioB)
                ag_duracao = ag.duracao_real or ag.servico.duracao_minutos
                ag_fim = ag.data_hora + timedelta(minutes=ag_duracao)
                if ag.data_hora < fim_desejado and ag_fim > inicio_desejado:
                    return True
            return False
            
        else:
            # Fallback para bater no banco caso não tenha cache (ex: validando 1 criação direta)
            qs = Agendamento.objects.filter(
                funcionario_id=funcionario_id,
                status__in=[
                    Agendamento.Status.AGENDADO,
                    Agendamento.Status.CONFIRMADO,
                    Agendamento.Status.EM_ANDAMENTO
                ],
                data_hora__lt=fim_desejado
            )
            if agendamento_ignorado_id:
                qs = qs.exclude(id=agendamento_ignorado_id)
                
            for ag in qs:
                ag_duracao = ag.duracao_real or ag.servico.duracao_minutos
                ag_fim = ag.data_hora + timedelta(minutes=ag_duracao)
                if ag.data_hora < fim_desejado and ag_fim > inicio_desejado:
                    return True
                    
            return False
