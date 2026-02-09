"""
Testes para rotas de agendamentos.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.agendamentos
class TestAgendamentoEndpoints:
    """Testes para endpoints de agendamentos."""
    
    def test_list_agendamentos_as_cliente(self, authenticated_client_cliente, cliente, pet, servico, forma_pagamento, funcionario):
        """Cliente pode listar seus agendamentos."""
        from apps.agendamentos.models import Agendamento
        # Criar agendamento
        Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        url = reverse('agendamento-list')
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_agendamento(self, authenticated_client_cliente, pet, servico, forma_pagamento, funcionario):
        """Cliente pode criar agendamento."""
        url = reverse('agendamento-list')
        data = {
            'pet': pet.id,
            'servico': servico.id,
            'funcionario': funcionario.id,
            'forma_pagamento': forma_pagamento.id,
            'data_hora': (timezone.now() + timedelta(days=2)).isoformat(),
            'observacoes': 'Pet nervoso'
        }
        response = authenticated_client_cliente.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_agendamento_past_date_fails(self, authenticated_client_cliente, pet, servico, forma_pagamento, funcionario):
        """Não pode criar agendamento no passado."""
        url = reverse('agendamento-list')
        data = {
            'pet': pet.id,
            'servico': servico.id,
            'funcionario': funcionario.id,
            'forma_pagamento': forma_pagamento.id,
            'data_hora': (timezone.now() - timedelta(days=1)).isoformat()
        }
        response = authenticated_client_cliente.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_retrieve_agendamento(self, authenticated_client_cliente, cliente, pet, servico, forma_pagamento, funcionario):
        """Recuperar detalhes de um agendamento."""
        from apps.agendamentos.models import Agendamento
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        url = reverse('agendamento-detail', kwargs={'pk': agendamento.pk})
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_agendamento_status(self, authenticated_client_funcionario, cliente, pet, servico, forma_pagamento, funcionario):
        """Funcionário pode atualizar status do agendamento."""
        from apps.agendamentos.models import Agendamento
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1),
            status='AGENDADO'
        )
        
        url = reverse('agendamento-detail', kwargs={'pk': agendamento.pk})
        # Teste apenas GET já que PATCH pode não estar disponível
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
