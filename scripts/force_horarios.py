import os
import sys
import django
from datetime import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.funcionarios.models import Funcionario, HorarioTrabalho

def forcar_horarios():
    print("Atualizando todos os funcionários ativos para trabalhar todos os dias...")
    funcionarios = Funcionario.objects.filter(ativo=True)
    
    # Limpa as escalas antigas para não dar conflito (unique_together no db)
    HorarioTrabalho.objects.all().delete()
    
    dias_criados = 0
    for func in funcionarios:
        print(f"Alocando agenda para o(a) {func.usuario.nome}...")
        for dia in range(7):
            try:
                HorarioTrabalho.objects.create(
                    funcionario=func,
                    dia_semana=dia,
                    hora_inicio=time(8, 0),
                    hora_fim=time(18, 0),
                    ativo=True
                )
                dias_criados += 1
            except Exception as e:
                print(f"Erro ao alocar dia {dia} para {func}: {e}")
                
    print(f"Pronto! {dias_criados} dias preenchidos na base.")

if __name__ == '__main__':
    forcar_horarios()
