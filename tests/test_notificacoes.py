"""
Testes para rotas de notificações.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.notificacoes
class TestNotificacaoEndpoints:
    """Testes para endpoints de notificações."""
    
    def test_list_notificacoes(self, authenticated_client_cliente):
        """Cliente pode listar suas notificações."""
        url = reverse('notificacao-list')
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_notificacao(self, authenticated_client_cliente, cliente, pet, servico, forma_pagamento, funcionario):
        """Recuperar detalhes de uma notificação."""
        from apps.notificacoes.models import Notificacao
        from apps.agendamentos.models import Agendamento
        from django.utils import timezone
        from datetime import timedelta
        
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo='CONFIRMACAO',
            canal='EMAIL',
            destinatario=cliente.usuario.email,
            assunto='Teste',
            mensagem='Mensagem de teste'
        )
        
        url = reverse('notificacao-detail', kwargs={'pk': notificacao.pk})
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assunto'] == 'Teste'
    
    def test_mark_as_read(self, authenticated_client_cliente, cliente, pet, servico, forma_pagamento, funcionario):
        """Marcar notificação como lida."""
        from apps.notificacoes.models import Notificacao
        from apps.agendamentos.models import Agendamento
        from django.utils import timezone
        from datetime import timedelta
        
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            pet=pet,
            servico=servico,
            funcionario=funcionario,
            forma_pagamento=forma_pagamento,
            data_hora=timezone.now() + timedelta(days=1)
        )
        
        notificacao = Notificacao.objects.create(
            agendamento=agendamento,
            tipo='LEMBRETE',
            canal='EMAIL',
            destinatario=cliente.usuario.email,
            assunto='Teste',
            mensagem='Mensagem de teste',
            lida=False
        )
        
        url = reverse('notificacao-detail', kwargs={'pk': notificacao.pk})
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assunto'] == 'Teste'
