# scripts/seed_funcionario.py
import os
import sys
import django
from datetime import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.authentication.models import Usuario
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from django.contrib.auth.models import Group

def criar_funcionario_teste():
    usuario, created = Usuario.objects.get_or_create(
        email='funcionario@test.com',
        defaults={
            'nome': 'João Tosador (Teste)',
            'telefone': '88977777777'
        }
    )
    if created:
        usuario.set_password('func123')
        usuario.save()
        
        func_group, _ = Group.objects.get_or_create(name='FUNCIONARIO')
        usuario.groups.add(func_group)
        
    funcionario, created_func = Funcionario.objects.get_or_create(
        usuario=usuario,
        defaults={
            'cargo': Funcionario.Cargo.TOSADOR,
            'horario_trabalho': 'Segunda a Domingo, 08:00-18:00'
        }
    )
    
    if created_func:
        print('✓ Funcionário teste criado: funcionario@test.com')
    else:
        print('✓ Funcionário teste já existia.')
        
    # Criar escala para todos os dias da semana (0 a 6) para garantir
    horas_criadas = 0
    for dia in range(7):
        horario, created_hora = HorarioTrabalho.objects.get_or_create(
            funcionario=funcionario,
            dia_semana=dia,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0)
        )
        if created_hora:
            horas_criadas += 1
            
    print(f'✓ {horas_criadas} dias de expediente cadastrados para o funcionário.')

if __name__ == '__main__':
    criar_funcionario_teste()
