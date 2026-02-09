"""
Fixtures compartilhadas para todos os testes.
"""
import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from apps.authentication.models import Usuario
from apps.clientes.models import Cliente
from apps.funcionarios.models import Funcionario
from apps.pets.models import Pet
from apps.servicos.models import Servico
from apps.pagamentos.models import FormaPagamento


@pytest.fixture
def api_client():
    """Cliente API para testes."""
    return APIClient()


@pytest.fixture
def grupo_cliente():
    """Grupo CLIENTE."""
    return Group.objects.get_or_create(name='CLIENTE')[0]


@pytest.fixture
def grupo_funcionario():
    """Grupo FUNCIONARIO."""
    return Group.objects.get_or_create(name='FUNCIONARIO')[0]


@pytest.fixture
def grupo_admin():
    """Grupo ADMINISTRADOR."""
    return Group.objects.get_or_create(name='ADMINISTRADOR')[0]


@pytest.fixture
def usuario_cliente(grupo_cliente):
    """Usuário do tipo Cliente."""
    user = Usuario.objects.create_user(
        email='cliente@test.com',
        senha='testpass123',
        nome='Cliente Teste',
        telefone='(88) 99999-9999'
    )
    user.groups.add(grupo_cliente)
    return user


@pytest.fixture
def usuario_funcionario(grupo_funcionario):
    """Usuário do tipo Funcionário."""
    user = Usuario.objects.create_user(
        email='funcionario@test.com',
        senha='testpass123',
        nome='Funcionário Teste',
        telefone='(88) 98888-8888'
    )
    user.groups.add(grupo_funcionario)
    return user


@pytest.fixture
def usuario_admin(grupo_admin):
    """Usuário do tipo Administrador."""
    user = Usuario.objects.create_superuser(
        email='admin@test.com',
        senha='testpass123',
        nome='Admin Teste',
        telefone='(88) 97777-7777'
    )
    return user


@pytest.fixture
def cliente(usuario_cliente):
    """Cliente completo."""
    return Cliente.objects.create(
        usuario=usuario_cliente,
        cpf='123.456.789-00',
        endereco='Rua Teste, 123',
        cidade='Sobral',
        estado='CE',
        cep='62000-000'
    )


@pytest.fixture
def funcionario(usuario_funcionario):
    """Funcionário completo."""
    return Funcionario.objects.create(
        usuario=usuario_funcionario,
        cargo='ATENDENTE',
        horario_trabalho='Segunda a Sexta, 08:00-17:00'
    )


@pytest.fixture
def pet(cliente):
    """Pet de teste."""
    return Pet.objects.create(
        cliente=cliente,
        nome='Rex',
        especie='CAO',
        raca='Labrador',
        idade=3,
        peso=25.5,
        observacoes='Dócil e brincalhão'
    )


@pytest.fixture
def servico():
    """Serviço de teste."""
    return Servico.objects.create(
        tipo='BANHO',
        descricao='Banho completo para cães',
        preco=50.00,
        duracao_minutos=60
    )


@pytest.fixture
def forma_pagamento():
    """Forma de pagamento de teste."""
    return FormaPagamento.objects.create(
        nome='Dinheiro',
        tipo='DINHEIRO',
        descricao='Pagamento em dinheiro'
    )


@pytest.fixture
def authenticated_client_cliente(api_client, usuario_cliente):
    """Cliente API autenticado como Cliente."""
    api_client.force_authenticate(user=usuario_cliente)
    return api_client


@pytest.fixture
def authenticated_client_funcionario(api_client, usuario_funcionario):
    """Cliente API autenticado como Funcionário."""
    api_client.force_authenticate(user=usuario_funcionario)
    return api_client


@pytest.fixture
def authenticated_client_admin(api_client, usuario_admin):
    """Cliente API autenticado como Admin."""
    api_client.force_authenticate(user=usuario_admin)
    return api_client
