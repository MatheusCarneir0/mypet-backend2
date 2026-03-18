import os
import sys

# Add the project directory to the sys.path
sys.path.append('c:/Users/Matheus/Documents/MyPet/mypet-backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.agendamentos.services import AgendamentoService
from apps.funcionarios.models import HorarioTrabalho
from datetime import datetime

print("== HORARIOS CADASTRADOS ==")
for h in HorarioTrabalho.objects.all():
    print(f"- {h.funcionario.usuario.nome}: Dia {h.dia_semana}, das {h.hora_inicio} as {h.hora_fim}")

print("\n== VAGAS PROXIMOS 3 DIAS ==")
for delta in range(0, 3):
    dt = (datetime.now() + datetime.timedelta(days=delta)).date()
    try:
        res = AgendamentoService.horarios_disponiveis(dt, 1) # Servico ID 1 (Geralmente Banho ou Consulta)
        print(f"[{dt}] Vagas disponiveis para Servico 1: {len(res)}")
        if len(res) > 0:
             print(f"Primeiros 3 slots: {res[:3]}")
    except Exception as e:
        print(f"Erro no dia {dt}: {e}")
