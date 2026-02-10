"""
Testes para rotas de pagamentos.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.pagamentos
class TestPagamentoEndpoints:
    """Testes para endpoints de pagamentos."""
    
    def test_list_transacoes_as_funcionario(self, authenticated_client_funcionario):
        """Funcionário pode listar transações."""
        url = reverse('transacao-pagamento-list')
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_transacao(self, authenticated_client_funcionario, cliente, pet, servico, forma_pagamento, funcionario):
        """Funcionário pode criar transação de pagamento via processar-dinheiro."""
        from apps.agendamentos.models import Agendamento
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        url = reverse('transacao-pagamento-processar-dinheiro')
        data = {
            'agendamento_id': agendamento.id,
            'valor': 50.00,
            'valor_recebido': 50.00,
            'observacoes': 'Pagamento em dinheiro'
        }
        response = authenticated_client_funcionario.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_retrieve_transacao(self, authenticated_client_funcionario, cliente, pet, servico, forma_pagamento, funcionario):
        """Recuperar detalhes de uma transação."""
        from apps.agendamentos.models import Agendamento
        from apps.pagamentos.models import TransacaoPagamento
        
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        transacao = TransacaoPagamento.objects.create(
            agendamento=agendamento,
            forma_pagamento=forma_pagamento,
            valor=50.00,
            status='CONFIRMADO'
        )
        
        url = reverse('transacao-pagamento-detail', kwargs={'pk': transacao.pk})
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['valor']) == 50.00
