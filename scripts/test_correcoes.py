import os
import sys
import django
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

# Config setup
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.servicos.models import Servico
from apps.agendamentos.models import Agendamento
from apps.funcionarios.models import Funcionario
from apps.clientes.models import Cliente
from apps.pets.models import Pet
from apps.authentication.models import Usuario

def run():
    print("Iniciando testes de verificação...")
    
    # 1. Teste de Serviços duplicados (Tipo)
    print("\n[1] Testando flexibilidade de tipos de Serviço...")
    try:
        s1 = Servico.objects.create(
            tipo='BANHO', 
            descricao='Banho P', 
            preco=50.00, 
            duracao_minutos=30
        )
        s2 = Servico.objects.create(
            tipo='BANHO', 
            descricao='Banho M', 
            preco=60.00, 
            duracao_minutos=40
        )
        print("✅ Sucesso: Doctos serviços com mesmo tipo criados.")
    except Exception as e:
        print(f"❌ Falha: Erro ao criar serviços duplicados: {e}")

    # 2. Teste de Conflito de Agendamento
    print("\n[2] Testando validação de conflito de horários...")
    try:
        # Pega ou cria fixtures
        user_func = Usuario.objects.filter(email='func_teste@email.com').first()
        if not user_func:
            user_func = Usuario.objects.create_user(email='func_teste@email.com', password='123', nome='Func Teste', telefone='123')
        
        func, _ = Funcionario.objects.get_or_create(usuario=user_func, defaults={'cargo': 'ATENDENTE', 'horario_trabalho': 'Comercial'})

        user_cli = Usuario.objects.filter(email='cli_teste@email.com').first()
        if not user_cli:
            user_cli = Usuario.objects.create_user(email='cli_teste@email.com', password='123', nome='Cli Teste', telefone='123')
            
        cliente, _ = Cliente.objects.get_or_create(usuario=user_cli, defaults={'cpf': '000.000.000-00', 'endereco': 'Rua A', 'cidade': 'Sobral', 'cep': '62000-000'})
        
        pet, _ = Pet.objects.get_or_create(cliente=cliente, nome='Rex', especie='CAO', raca='Vira-lata', idade=2, peso=10)
        
        # Pagamento (Forma)
        from apps.pagamentos.models import FormaPagamento
        forma_pag, _ = FormaPagamento.objects.get_or_create(nome='Dinheiro', tipo='DINHEIRO')

        # Agendamento 1: Hoje as 14:00 (duracao 30min - vai até 14:30)
        hoje_14h = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1) # Amanhã para garantir futuro
        
        ag1 = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=s1, # 30 min
            funcionario=func,
            forma_pagamento=forma_pag,
            data_hora=hoje_14h
        )
        print(f"   Agendamento 1 criado: {hoje_14h} (Duração: {s1.duracao_minutos}min)")

        # Tentativa de Agendamento 2: Começando 14:15 (Overlap!)
        horario_conflito = hoje_14h + timedelta(minutes=15)
        print(f"   Tentando criar Agendamento 2 (Conflito): {horario_conflito}...")
        
        ag2 = Agendamento(
            cliente=cliente,
            pet=pet,
            servico=s1, 
            funcionario=func,
            forma_pagamento=forma_pag,
            data_hora=horario_conflito
        )
        ag2.full_clean()
        ag2.save()
        print("❌ Falha: O sistema permitiu agendamento conflitante!")
        
    except ValidationError as e:
        print(f"✅ Sucesso: O sistema bloqueou o conflito corretamente:\n   {e.message_dict if hasattr(e, 'message_dict') else e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

    # Limpeza
    print("\nLimpando dados de teste...")
    try:
        if 's1' in locals(): s1.delete()
        if 's2' in locals(): s2.delete()
        if 'ag1' in locals(): ag1.delete()
        # Users/Func/Cli/Pet cleans up via cascade or leave as persistent fixtures in dev
    except:
        pass

if __name__ == '__main__':
    run()
