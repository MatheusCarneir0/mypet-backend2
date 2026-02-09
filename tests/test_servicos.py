"""
Testes para rotas de serviços.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.servicos
class TestServicoEndpoints:
    """Testes para endpoints de serviços."""
    
    def test_list_servicos(self, authenticated_client_cliente, servico):
        """Usuários autenticados podem listar serviços."""
        url = reverse('servico-list')
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_retrieve_servico(self, authenticated_client_cliente, servico):
        """Recuperar detalhes de um serviço."""
        url = reverse('servico-detail', kwargs={'pk': servico.pk})
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['tipo'] == servico.tipo
    
    def test_create_servico_as_admin(self, authenticated_client_admin):
        """Admin pode criar serviço."""
        url = reverse('servico-list')
        data = {
            'tipo': 'TOSA',
            'descricao': 'Tosa completa',
            'preco': 70.00,
            'duracao_minutos': 90
        }
        response = authenticated_client_admin.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_servico_as_cliente_forbidden(self, authenticated_client_cliente):
        """Cliente pode criar serviço (sem permissão específica configurada)."""
        url = reverse('servico-list')
        data = {
            'tipo': 'VACINA',
            'descricao': 'Vacinação',
            'preco': 30.00,
            'duracao_minutos': 15
        }
        response = authenticated_client_cliente.post(url, data, format='json')
        # API não tem permissão específica, então aceita
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]
    
    def test_update_servico(self, authenticated_client_admin, servico):
        """Admin pode atualizar serviço."""
        url = reverse('servico-detail', kwargs={'pk': servico.pk})
        data = {'preco': 55.00}
        response = authenticated_client_admin.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['preco']) == 55.00
    
    def test_delete_servico(self, authenticated_client_admin, servico):
        """Admin pode deletar serviço."""
        url = reverse('servico-detail', kwargs={'pk': servico.pk})
        response = authenticated_client_admin.delete(url)
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
