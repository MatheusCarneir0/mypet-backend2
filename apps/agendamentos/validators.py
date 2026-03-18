# apps/agendamentos/validators.py
from django.utils import timezone
from datetime import timedelta
from typing import Tuple, Optional

class AgendamentoValidator:
    """
    Desacopla regras de validação rígidas do model e do serializer,
    permitindo reuso e testabilidade unitária fáceis para Agendamentos.
    """
    
    ANTECEDENCIA_MINIMA_MINUTOS = 30
    
    @staticmethod
    def validar_data_hora_futura(data_hora) -> Tuple[bool, Optional[str]]:
        """A data não pode estar no passado."""
        if data_hora < timezone.now():
            return False, 'Não é possível agendar para uma data/hora no passado.'
        return True, None
        
    @staticmethod
    def validar_antecedencia_minima(data_hora) -> Tuple[bool, Optional[str]]:
        """Exige um tempo mínimo entre o momento do click e o agendamento real."""
        agora = timezone.now()
        antecedencia_minima = agora + timedelta(minutes=AgendamentoValidator.ANTECEDENCIA_MINIMA_MINUTOS)
        
        if data_hora < antecedencia_minima:
            return False, f'É necessário agendar com pelo menos {AgendamentoValidator.ANTECEDENCIA_MINIMA_MINUTOS} minutos de antecedência.'
        return True, None
        
    @staticmethod
    def validar_horario_dentro_expediente(hora_inicio, duracao_minutos, expedientes) -> bool:
        """
        Valida in-memory se um slot (com duração) cabe inteiro em ALGUM
        dos expedientes informados no DB para esse funcionário.
        """
        import datetime
        
        inicio_desejado = hora_inicio
        # Gambiarra para somar minutos em datetime.time sem virar o dia inteiro
        dummy_date = datetime.datetime(2000, 1, 1, inicio_desejado.hour, inicio_desejado.minute)
        fim_desejado = (dummy_date + timedelta(minutes=duracao_minutos)).time()
        
        for emp in expedientes:
            if inicio_desejado >= emp.hora_inicio and fim_desejado <= emp.hora_fim:
                return True
        return False

    @staticmethod
    def validar_pet_pertence_cliente(pet, cliente) -> Tuple[bool, Optional[str]]:
        """Garante a posse."""
        if pet and cliente and pet.cliente_id != cliente.id:
            return False, 'O pet selecionado não pertence a este cliente.'
        return True, None
