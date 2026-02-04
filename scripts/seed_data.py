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
    admin, created = Usuario.objects.get_or_create(
        email='admin@farmavet.com',
        defaults={
            'nome': 'Administrador FarmaVet',
            'telefone': '88999999999',
            'tipo_usuario': Usuario.TipoUsuario.ADMINISTRADOR,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print('✓ Admin criado: admin@farmavet.com / admin123')


def criar_servicos():
    """Cria serviços padrão."""
    servicos = [
        {
            'tipo': Servico.TipoServico.BANHO,
            'descricao': 'Banho completo com shampoo especial',
            'preco': 50.00,
            'duracao_minutos': 60
        },
        {
            'tipo': Servico.TipoServico.TOSA,
            'descricao': 'Tosa higiênica ou estética',
            'preco': 70.00,
            'duracao_minutos': 90
        },
        {
            'tipo': Servico.TipoServico.BANHO_TOSA,
            'descricao': 'Banho completo + tosa',
            'preco': 100.00,
            'duracao_minutos': 120
        },
        {
            'tipo': Servico.TipoServico.VETERINARIO,
            'descricao': 'Consulta veterinária',
            'preco': 150.00,
            'duracao_minutos': 30
        },
    ]
    
    for servico_data in servicos:
        Servico.objects.get_or_create(
            tipo=servico_data['tipo'],
            defaults=servico_data
        )
    
    print(f'✓ {len(servicos)} serviços criados')


def criar_formas_pagamento():
    """Cria formas de pagamento padrão."""
    formas = [
        {
            'nome': 'Dinheiro',
            'tipo': FormaPagamento.TipoPagamento.DINHEIRO,
            'descricao': 'Pagamento em dinheiro'
        },
        {
            'nome': 'Cartão de Débito',
            'tipo': FormaPagamento.TipoPagamento.CARTAO_DEBITO,
            'descricao': 'Pagamento com cartão de débito'
        },
        {
            'nome': 'Cartão de Crédito',
            'tipo': FormaPagamento.TipoPagamento.CARTAO_CREDITO,
            'descricao': 'Pagamento com cartão de crédito'
        },
        {
            'nome': 'PIX',
            'tipo': FormaPagamento.TipoPagamento.PIX,
            'descricao': 'Pagamento via PIX'
        },
        {
            'nome': 'Pagar na Loja',
            'tipo': FormaPagamento.TipoPagamento.DINHEIRO,
            'descricao': 'Pagamento a ser realizado no estabelecimento'
        },
        {
            'nome': 'Pagar na Entrega',
            'tipo': FormaPagamento.TipoPagamento.DINHEIRO,
            'descricao': 'Pagamento a ser realizado no momento da entrega'
        },
    ]
    
    for forma_data in formas:
        FormaPagamento.objects.get_or_create(
            nome=forma_data['nome'],
            defaults=forma_data
        )
    
    print(f'✓ {len(formas)} formas de pagamento criadas')


def criar_cliente_teste():
    """Cria cliente de teste."""
    usuario, created = Usuario.objects.get_or_create(
        email='cliente@test.com',
        defaults={
            'nome': 'Cliente Teste',
            'telefone': '88988888888',
            'tipo_usuario': Usuario.TipoUsuario.CLIENTE
        }
    )
    if created:
        usuario.set_password('cliente123')
        usuario.save()
        
        Cliente.objects.create(
            usuario=usuario,
            cpf='123.456.789-00',
            endereco='Rua Teste, 123',
            cidade='Boa Viagem',
            estado='CE',
            cep='63870-000'
        )
        
        print('✓ Cliente teste criado: cliente@test.com / cliente123')


def main():
    """Executa todos os seeds."""
    print('🌱 Populando banco de dados...\n')
    
    criar_admin()
    criar_servicos()
    criar_formas_pagamento()
    criar_cliente_teste()
    
    print('\n✅ Banco de dados populado com sucesso!')


if __name__ == '__main__':
    main()

