import os
import django
from datetime import date, timedelta
import sys

# Setting up django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.funcionarios.models import Funcionario, HorarioTrabalho
from apps.servicos.models import Servico
from apps.agendamentos.services import AgendamentoService

def run():
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        amanha = date.today() + timedelta(days=1)
        
        f.write(f"TESTING FOR {amanha}\n\n")
        f.write("SERVIÇOS:\n")
        
        for s in Servico.objects.filter(ativo=True):
            f.write(f"  - ID: {s.id} | Tipo: {s.tipo} | Duracao: {s.duracao_minutos}\n")

        f.write("\nFUNCIONÁRIOS:\n")
        for func in Funcionario.objects.filter(ativo=True):
            f.write(f"  - ID: {func.id} | Nome: {func.usuario.nome} | Cargo: {func.cargo}\n")

        f.write("\nHORÁRIOS DE TRABALHO:\n")
        for h in HorarioTrabalho.objects.filter(ativo=True):
            f.write(f"  - Func: {h.funcionario.usuario.nome} | Dia: {h.dia_semana} | "
                    f"Das {h.hora_inicio} às {h.hora_fim}\n")

        s1 = Servico.objects.filter(ativo=True).first()
        if s1:
            f.write(f"\nTESTANDO DISPONIBILIDADE DO SERVICO ID {s1.id} ({s1.tipo})\n")
            try:
                horarios = AgendamentoService.horarios_disponiveis(amanha, s1.id)
                f.write(f"Resultado horarios_disponiveis:\n{horarios}\n")
            except Exception as e:
                f.write(f"ERRO: {str(e)}\n")
        else:
            f.write("\nNENHUM SERVICO ENCONTRADO.\n")

if __name__ == '__main__':
    run()
