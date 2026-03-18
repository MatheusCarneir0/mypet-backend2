"""Simulate the exact user flow to find the bug."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.agendamentos.services import AgendamentoService
from apps.agendamentos.models import Agendamento
from apps.agendamentos.repositories import AgendamentoRepository
from apps.clientes.models import Cliente
from apps.servicos.models import Servico
from apps.pets.models import Pet
from apps.pagamentos.models import FormaPagamento
from django.utils import timezone
from datetime import datetime, timedelta, date

# Exact scenario: Banho Tosa, 13/03/2026, 07:00
target_date = date(2026, 3, 13)
target_time = datetime.strptime('07:00', '%H:%M').time()
data_hora = timezone.make_aware(datetime.combine(target_date, target_time))

cliente = Cliente.objects.get(id=1)
pet_juca = Pet.objects.get(id=3)  # juca, MINI
servico_banho_tosa = Servico.objects.get(tipo='BANHO_TOSA')
forma = FormaPagamento.objects.first()

duracao = AgendamentoService.obter_duracao_servico(servico_banho_tosa, pet_juca)
print(f'=== Setup ===')
print(f'Pet: {pet_juca.nome} (porte={pet_juca.porte})')
print(f'Servico: {servico_banho_tosa.tipo} duracao={duracao}min')
print(f'Data/Hora: {target_date} 07:00')
print()

# Check if there are any existing agendamentos for 13/03
print('=== Agendamentos existentes para 13/03 ===')
from datetime import time
inicio_dia = timezone.make_aware(datetime.combine(target_date, time.min))
fim_dia = timezone.make_aware(datetime.combine(target_date, time.max))
existing = Agendamento.objects.filter(
    data_hora__gte=inicio_dia, data_hora__lt=fim_dia,
    status__in=['AGENDADO','CONFIRMADO','EM_ANDAMENTO']
).select_related('pet','servico','funcionario')
for a in existing:
    print(f'  id={a.id} {a.data_hora.strftime("%H:%M")} pet={a.pet.nome} serv={a.servico.tipo} dur={a.duracao_real} func={a.funcionario}')
if not existing:
    print('  Nenhum')

# Step 1: Check availability BEFORE booking
print()
print('=== Disponibilidade ANTES (pet_id=3) ===')
slots = AgendamentoService.horarios_disponiveis(target_date, servico_banho_tosa.id, pet_id=pet_juca.id)
for s in slots:
    if s['hora'] in ['07:00','07:30','08:00','08:30','09:00','09:30']:
        tag = 'LIVRE' if s['disponivel'] else 'OCUPADO'
        print(f"  {s['hora']}: {tag}")

# Step 2: Create first booking
print()
print('=== Criando agendamento 1: juca 07:00 ===')
ag1 = AgendamentoService.criar_agendamento(
    cliente=cliente, pet_id=pet_juca.id, servico_id=servico_banho_tosa.id,
    data_hora=data_hora, forma_pagamento_id=forma.id, observacoes='Teste 1'
)
print(f'OK: id={ag1.id}, func={ag1.funcionario}, duracao_real={ag1.duracao_real}')

# Step 3: Check availability AFTER (same pet)
print()
print('=== Disponibilidade DEPOIS (pet_id=3, juca) ===')
slots2 = AgendamentoService.horarios_disponiveis(target_date, servico_banho_tosa.id, pet_id=pet_juca.id)
for s in slots2:
    if s['hora'] in ['07:00','07:30','08:00','08:30','09:00','09:30']:
        tag = 'LIVRE' if s['disponivel'] else 'OCUPADO'
        print(f"  {s['hora']}: {tag}")

# Step 4: Check availability for DIFFERENT pet (Jao, id=2) same client
print()
print('=== Disponibilidade DEPOIS (pet_id=2, Jao) ===')
pet_jao = Pet.objects.get(id=2)
slots3 = AgendamentoService.horarios_disponiveis(target_date, servico_banho_tosa.id, pet_id=pet_jao.id)
for s in slots3:
    if s['hora'] in ['07:00','07:30','08:00','08:30','09:00','09:30']:
        tag = 'LIVRE' if s['disponivel'] else 'OCUPADO'
        print(f"  {s['hora']}: {tag}")

# Step 5: Check availability WITHOUT pet_id (like the frontend might be doing)
print()
print('=== Disponibilidade DEPOIS (SEM pet_id) ===')
slots4 = AgendamentoService.horarios_disponiveis(target_date, servico_banho_tosa.id, pet_id=None)
for s in slots4:
    if s['hora'] in ['07:00','07:30','08:00','08:30','09:00','09:30']:
        tag = 'LIVRE' if s['disponivel'] else 'OCUPADO'
        print(f"  {s['hora']}: {tag}")

# Step 6: Try to create second booking
print()
print('=== Tentando criar agendamento 2: juca 07:00 ===')
try:
    ag2 = AgendamentoService.criar_agendamento(
        cliente=cliente, pet_id=pet_juca.id, servico_id=servico_banho_tosa.id,
        data_hora=data_hora, forma_pagamento_id=forma.id, observacoes='Teste 2'
    )
    print(f'FALHA: Duplicou! id={ag2.id}')
    ag2.delete()
except Exception as e:
    print(f'OK BLOQUEADO: {e}')

# Step 7: Try different pet same client
print()
print('=== Tentando criar agendamento Jao 07:00 (mesmo cliente) ===')
try:
    ag3 = AgendamentoService.criar_agendamento(
        cliente=cliente, pet_id=pet_jao.id, servico_id=servico_banho_tosa.id,
        data_hora=data_hora, forma_pagamento_id=forma.id, observacoes='Teste 3'
    )
    print(f'FALHA: Duplicou! id={ag3.id}')
    ag3.delete()
except Exception as e:
    print(f'OK BLOQUEADO: {e}')

# Cleanup
ag1.delete()
print()
print('=== Teste completo ===')
