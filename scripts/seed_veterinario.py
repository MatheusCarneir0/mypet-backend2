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

def criar_func():
    usuario, _ = Usuario.objects.get_or_create(
        email='vet@test.com',
        defaults={'nome': 'Dra. Ana (Veterinária)', 'telefone': '88966666666'}
    )
    usuario.set_password('vet123')
    usuario.save()
        
    func_group, _ = Group.objects.get_or_create(name='FUNCIONARIO')
    usuario.groups.add(func_group)
        
    funcionario, _ = Funcionario.objects.get_or_create(
        usuario=usuario,
        defaults={'cargo': Funcionario.Cargo.VETERINARIO, 'horario_trabalho': 'Segunda a Domingo, 08:00-18:00'}
    )
    
    for dia in range(7):
        HorarioTrabalho.objects.get_or_create(
            funcionario=funcionario,
            dia_semana=dia,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0)
        )
    print('Veterinario criado com expedientes.')

if __name__ == '__main__':
    criar_func()
