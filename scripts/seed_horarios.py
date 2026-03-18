import os
import sys
import django
from datetime import date, time

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.authentication.models import Usuario
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.servicos.models import Servico
from apps.agendamentos.services import AgendamentoService
from django.contrib.auth.models import Group

def run_test():
    print("Criando funcionario tosador...")
    grupo, _ = Group.objects.get_or_create(name='FUNCIONARIO')
    
    usuario, _ = Usuario.objects.get_or_create(
        email='tosador@farmavet.com',
        defaults={'nome': 'Tosador Teste', 'telefone': '111111'}
    )
    usuario.groups.add(grupo)

    tosador, _ = Funcionario.objects.get_or_create(
        usuario=usuario,
        defaults={'cargo': Funcionario.Cargo.TOSADOR, 'horario_trabalho': '8h as 18h'}
    )

    print("Definindo expediente: Segunda-feira, 10:00 as 14:00")
    HorarioTrabalho.objects.filter(funcionario=tosador).delete()
    HorarioTrabalho.objects.create(
        funcionario=tosador,
        dia_semana=1, # Segunda-feira na nossa modelagem DB 
        hora_inicio=time(10, 0),
        hora_fim=time(14, 0)
    )

    # Segunda-feira
    data_teste = date(2026, 3, 2) # Uma segunda-feira
    
    servico = Servico.objects.filter(tipo=Servico.TipoServico.TOSA).first()
    if not servico:
        print("Erro: Servico de tosa não encontrado.")
        return

    horarios_disp = AgendamentoService.horarios_disponiveis(data_teste, servico.id)
    print(f"Horários disponíveis para TOSA em {data_teste} (Esperado 10h as 14h exceto o último slot se não couber):")
    for h in horarios_disp:
        if h['disponivel']:
            print(f" - {h['hora']} (Disponível)")

if __name__ == '__main__':
    run_test()
