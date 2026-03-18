# apps/agendamentos/tests.py
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.utils import timezone
from datetime import timedelta, date, time

from apps.pets.models import Pet
from apps.servicos.models import Servico
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.agendamentos.models import Agendamento
from apps.agendamentos.services import AgendamentoService
from apps.usuarios.models import Usuario
from apps.clientes.models import Cliente
from apps.pagamentos.models import FormaPagamento

class AgendamentoServiceTests(TestCase):
    
    def setUp(self):
        # Setup base objects
        self.servico = Servico.objects.create(
            tipo=Servico.TipoServico.BANHO, 
            descricao='Banho Básico', 
            preco=50.00, 
            duracao_minutos=30
        )
        self.forma_pagamento = FormaPagamento.objects.create(
            nome='PIX', 
            tipo='PIX'
        )

        user1 = Usuario.objects.create(email='cli1@test.com', nome='Cliente 1')
        user2 = Usuario.objects.create(email='func1@test.com', nome='Funcionario 1')
        
        self.cliente = Cliente.objects.create(usuario=user1)
        self.pet = Pet.objects.create(
            cliente=self.cliente, 
            nome='Rex', 
            especie=Pet.Especie.CAO, 
            idade=2, 
            peso=10
        )
        
        self.funcionario = Funcionario.objects.create(
            usuario=user2, 
            cargo=Funcionario.Cargo.ATENDENTE
        )
        
        # O teste rodará usando "hoje"
        self.hoje = timezone.localtime().date()
        # O MySQL tem dia da semana começando em Domingo (1). Python começa em segunda (0).
        # A lógica do service usa: (data.weekday() + 1) % 7
        # Python: 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sab, 6=Dom
        # Banco nosso: 1=Seg, 2=Ter, ..., 0=Dom (?) 
        # Note: _get_dia_semana_bd is (data.weekday() + 1) % 7 -> python 6 (dom) + 1 = 7 % 7 = 0. Python 0(seg)+1=1. 
        self.dia_semana_bd = AgendamentoService._get_dia_semana_bd(self.hoje)
        
        # Expediente pro dia todo (08:00 - 18:00)
        HorarioTrabalho.objects.create(
            funcionario=self.funcionario,
            dia_semana=self.dia_semana_bd,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0)
        )

    def test_horarios_disponiveis_query_count(self):
        """Assegura que a listagem de slots resolve sem N+1 queries"""
        
        # Test 1: Sem agendamentos criados
        with CaptureQueriesContext(connection) as ctx:
            slots = AgendamentoService.horarios_disponiveis(self.hoje, self.servico.id)
            
        # As queries num cenário ideal vazio deveriam ser:
        # 1. Servico
        # 2. Funcionarios in (Prefetch) -> Isso pode gerar 2 queries (1 de subquery Func, 1 prefetch Horario)
        # 3. Agendamentos in
        self.assertLessEqual(len(ctx.captured_queries), 5, f"Estourou queries limit, total executadas: {len(ctx.captured_queries)}")
        self.assertTrue(len(slots) > 0)
        
    def test_verificar_conflito_ocupacao(self):
        """Garante que criar agendamento retira aquele slot da listagem"""
        inicio = timezone.make_aware(timezone.datetime.combine(self.hoje, time(10, 0)))
        
        # Ocupando as 10:00
        AgendamentoService.criar_agendamento(
            cliente=self.cliente,
            pet_id=self.pet.id,
            servico_id=self.servico.id,
            data_hora=inicio,
            forma_pagamento_id=self.forma_pagamento.id
        )
        
        slots = AgendamentoService.horarios_disponiveis(self.hoje, self.servico.id)
        # O '10:00' deve vir com { ... disponivel: False } ou totalmente fora!
        # Pelo código da API, listamos is_livre nos return
        slot_10 = next((s for s in slots if s['hora'] == '10:00'), None)
        
        if slot_10 is not None:
             self.assertFalse(slot_10['disponivel'])
             
    def test_horario_domingo_e_aceito(self):
        """Se HorarioTrabalho for persistido num domingo, deve gerar slots normalmente, removendo regra hardcoded"""
        domingo_date = date(2027, 8, 1) # É um domingo, 2027-08-01
        self.assertEqual(domingo_date.weekday(), 6) # Confirmação
        
        dia_semana_bd_domingo = AgendamentoService._get_dia_semana_bd(domingo_date)
        
        HorarioTrabalho.objects.create(
            funcionario=self.funcionario,
            dia_semana=dia_semana_bd_domingo,
            hora_inicio=time(10, 0),
            hora_fim=time(14, 0) # Meio expediente
        )
        
        # Sem N+1
        with CaptureQueriesContext(connection) as ctx:
            slots = AgendamentoService.horarios_disponiveis(domingo_date, self.servico.id)
            
        self.assertTrue(any(s['hora'] == '10:00' and s['disponivel'] for s in slots))
