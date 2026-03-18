# apps/funcionarios/management/commands/criar_horarios_padrao.py
from django.core.management.base import BaseCommand
from apps.funcionarios.models import Funcionario, HorarioTrabalho
from datetime import time

class Command(BaseCommand):
    help = 'Cria os registros básicos na escala de HorarioTrabalho para cada fucionario ativo (Seg-Sex, 08:00 - 18:00) caso esteja vazio.'

    def handle(self, *args, **options):
        funcionarios = Funcionario.objects.filter(ativo=True)
        criados = 0
        mantidos = 0
        
        for func in funcionarios:
            # Checar se já possui escala
            if HorarioTrabalho.objects.filter(funcionario=func).exists():
                mantidos += 1
                continue
                
            # Adicionar Segunda(1) a Sexta(5)
            for dia in [1, 2, 3, 4, 5]:
                HorarioTrabalho.objects.get_or_create(
                    funcionario=func,
                    dia_semana=dia,
                    hora_inicio=time(8, 0),
                    hora_fim=time(18, 0)
                )
            criados += 1
            
        self.stdout.write(self.style.SUCCESS(f'Escalas geradas. Criados para {criados} funcionários. Ignorados/Mantidos: {mantidos}.'))
