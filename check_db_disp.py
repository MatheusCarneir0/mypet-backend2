import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypet.settings')
django.setup()

from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.servicos.models import Servico
from apps.agendamentos.services import AgendamentoService
from datetime import date, timedelta

print("--- FUNCIONARIOS ---")
for f in Funcionario.objects.filter(ativo=True):
    print(f"ID: {f.id}, Nome: {f.usuario.nome}, Cargo: {f.cargo}")

print("\n--- SERVICOS ---")
for s in Servico.objects.filter(ativo=True):
    print(f"ID: {s.id}, Tipo: {s.tipo}, Duracao: {s.duracao_minutos}m")

print("\n--- HORARIOS TRABALHO ---")
for h in HorarioTrabalho.objects.filter(ativo=True):
    print(f"Funcionario: {h.funcionario.usuario.nome}, Dia: {h.dia_semana}, Das {h.hora_inicio} as {h.hora_fim}")

print("\n--- TESTE DISPONIBILIDADE (Hoje + 1) ---")
try:
    amanha = date.today() + timedelta(days=1)
    # Testa com servico de id 1 ou o primeiro existente
    s1 = Servico.objects.filter(ativo=True).first()
    if s1:
        horarios = AgendamentoService.horarios_disponiveis(amanha, s1.id)
        print(f"Data: {amanha} (Dia Semana BD: {AgendamentoService._get_dia_semana_bd(amanha)})")
        print(f"Servico ID: {s1.id}")
        print(f"Horarios Disponiveis encontrados:")
        for h in horarios:
            print(h)
    else:
        print("Nenhum servico ativo.")
except Exception as e:
    print("Erro testando disponibilidade:", e)
