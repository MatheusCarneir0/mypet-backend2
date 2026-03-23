# scripts/seed_data.py
"""
Script para popular banco de dados com dados de teste.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.authentication.models import Usuario
from apps.clientes.models import Cliente
from apps.servicos.models import Servico
from apps.funcionarios.models import Funcionario
from apps.pagamentos.models import FormaPagamento


def criar_admin():
    """Cria usuário administrador."""
    from django.contrib.auth.models import Group
    
    admin, created = Usuario.objects.get_or_create(
        email='admin@farmavet.com',
        defaults={
            'nome': 'Administrador FarmaVet',
            'telefone': '88999999999',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        
        admin_group, _ = Group.objects.get_or_create(name='ADMINISTRADOR')
        admin.groups.add(admin_group)
        
        print('✓ Admin criado: admin@farmavet.com / admin123')


def criar_servicos():
    """Cria serviços padrão da FarmaVet com os cargos vinculados."""
    from apps.servicos.models import ServicoCargo

    servicos = [
        {
            'nome': 'Banho',
            'descricao': 'Banho completo com shampoo especial.',
            'preco': 50.00,
            'duracao_minutos': 40,
            'cargos': ['ATENDENTE'],
        },
        {
            'nome': 'Tosa',
            'descricao': 'Tosa higiênica ou estética.',
            'preco': 70.00,
            'duracao_minutos': 80,
            'cargos': ['TOSADOR'],
        },
        {
            'nome': 'Banho e Tosa',
            'descricao': 'Banho completo + tosa.',
            'preco': 100.00,
            'duracao_minutos': 120,
            'cargos': ['TOSADOR', 'ATENDENTE'],
        },
        {
            'nome': 'Corte de Unhas',
            'descricao': 'Corte de unhas para pets de qualquer porte.',
            'preco': 25.00,
            'duracao_minutos': 15,
            'cargos': ['TOSADOR'],
        },
        {
            'nome': 'Banho Terapêutico',
            'descricao': 'Banho com produtos medicamentosos para tratamento de pele.',
            'preco': 80.00,
            'duracao_minutos': 50,
            'cargos': ['ATENDENTE'],
        },
        {
            'nome': 'Consulta Veterinária',
            'descricao': 'Atendimento com médico veterinário.',
            'preco': 150.00,
            'duracao_minutos': 30,
            'cargos': ['VETERINARIO'],
        },
    ]

    for servico_data in servicos:
        cargos = servico_data.pop('cargos')
        servico, _ = Servico.objects.update_or_create(
            nome=servico_data['nome'],
            defaults=servico_data
        )
        # Atualizar cargos vinculados
        ServicoCargo.objects.filter(servico=servico).delete()
        for cargo in cargos:
            ServicoCargo.objects.create(servico=servico, cargo=cargo)

    print(f'✓ {len(servicos)} serviços criados/atualizados')


def criar_formas_pagamento():
    """Cria formas de pagamento padrão: Dinheiro, PIX e Cartão."""
    formas = [
        {
            'nome': 'Dinheiro',
            'tipo': FormaPagamento.TipoPagamento.DINHEIRO,
            'descricao': 'Pagamento em dinheiro'
        },
        {
            'nome': 'PIX',
            'tipo': FormaPagamento.TipoPagamento.PIX,
            'descricao': 'Pagamento via PIX'
        },
        {
            'nome': 'Cartão',
            'tipo': FormaPagamento.TipoPagamento.CARTAO_CREDITO,
            'descricao': 'Pagamento com cartão (débito ou crédito)'
        },
    ]
    
    for forma_data in formas:
        FormaPagamento.objects.update_or_create(
            nome=forma_data['nome'],
            defaults=forma_data
        )
    
    print(f'✓ {len(formas)} formas de pagamento criadas/atualizadas')


def criar_cliente_teste():
    """Cria cliente de teste."""
    from django.contrib.auth.models import Group
    
    usuario, created = Usuario.objects.get_or_create(
        email='cliente@test.com',
        defaults={
            'nome': 'Cliente Teste',
            'telefone': '88988888888'
        }
    )
    if created:
        usuario.set_password('cliente123')
        usuario.save()
        
        cliente_group, _ = Group.objects.get_or_create(name='CLIENTE')
        usuario.groups.add(cliente_group)
        
        Cliente.objects.create(
            usuario=usuario,
            cpf='123.456.789-00',
            endereco='Rua Teste, 123',
            ponto_referencia='Próximo ao mercado central',
            cidade='Boa Viagem',
            estado='CE',
            cep='63870-000'
        )
        
        print('✓ Cliente teste criado: cliente@test.com / cliente123')


def criar_funcionario_teste():
    """Cria funcionário de teste (tosador)."""
    from django.contrib.auth.models import Group

    usuario, created = Usuario.objects.get_or_create(
        email='funcionario@test.com',
        defaults={
            'nome': 'Funcionário Teste',
            'telefone': '88977777777'
        }
    )
    if created:
        usuario.set_password('func123')
        usuario.save()

        func_group, _ = Group.objects.get_or_create(name='FUNCIONARIO')
        usuario.groups.add(func_group)

        Funcionario.objects.create(
            usuario=usuario,
            cargo=Funcionario.Cargo.TOSADOR,
            horario_trabalho='Segunda a Sábado, 07:00-17:30'
        )

        print('✓ Funcionário teste criado: funcionario@test.com / func123')
    else:
        print('  Funcionário teste já existe')


def regenerar_horarios_trabalho():
    """Re-salva todos os funcionários para regenerar HorarioTrabalho com intervalo de almoço."""
    count = 0
    for func in Funcionario.objects.all():
        func.save()
        count += 1
    print(f'✓ Horários de trabalho regenerados para {count} funcionário(s)')


def main():
    """Executa todos os seeds."""
    print('🌱 Populando banco de dados...\n')
    
    criar_admin()
    criar_servicos()
    criar_formas_pagamento()
    criar_cliente_teste()
    criar_funcionario_teste()
    regenerar_horarios_trabalho()
    
    print('\n✅ Banco de dados populado com sucesso!')


if __name__ == '__main__':
    main()

