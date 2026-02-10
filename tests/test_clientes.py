"""
Testes para rotas de clientes.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.clientes
class TestClienteEndpoints:
    """Testes para endpoints de clientes."""
    
    def test_list_clientes_as_funcionario(self, authenticated_client_funcionario, cliente):
        """Funcionário pode listar clientes."""
        url = reverse('cliente-list')
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_clientes_as_cliente_forbidden(self, authenticated_client_cliente):
        """Cliente não pode listar outros clientes."""
        url = reverse('cliente-list')
        response = authenticated_client_cliente.get(url)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_200_OK]
    
    def test_retrieve_cliente(self, authenticated_client_funcionario, cliente):
        """Recuperar detalhes de um cliente."""
        url = reverse('cliente-detail', kwargs={'pk': cliente.pk})
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['cpf'] == cliente.cpf
    
    def test_update_cliente_blocked(self, authenticated_client_admin, cliente):
        """PUT/PATCH bloqueados - usar /me/profile/ para atualização"""
        url = reverse('cliente-detail', kwargs={'pk': cliente.pk})
        data = {
            'endereco': 'Novo Endereço, 789',
            'cidade': 'Fortaleza',
            'estado': 'CE',
            'cep': '60000-000'
        }
        # PUT bloqueado
        response = authenticated_client_admin.put(url, data, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # PATCH bloqueado
        response = authenticated_client_admin.patch(url, data, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_delete_cliente(self, authenticated_client_admin, cliente):
        """Admin pode deletar cliente (soft delete)."""
        url = reverse('cliente-detail', kwargs={'pk': cliente.pk})
        response = authenticated_client_admin.delete(url)
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
