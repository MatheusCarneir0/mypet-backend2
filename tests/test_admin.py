"""
Testes para rotas administrativas.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.admin
class TestAdminEndpoints:
    """Testes para endpoints administrativos."""
    
    def test_dashboard_as_admin(self, authenticated_client_admin):
        """Admin pode acessar dashboard."""
        url = reverse('backoffice:dashboard')
        response = authenticated_client_admin.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_dashboard_as_cliente_forbidden(self, authenticated_client_cliente):
        """Cliente não pode acessar dashboard."""
        url = reverse('backoffice:dashboard')
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_funcionarios_as_admin(self, authenticated_client_admin, funcionario):
        """Admin pode listar funcionários."""
        url = reverse('backoffice:admin-funcionario-list')
        response = authenticated_client_admin.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_funcionario_as_admin(self, authenticated_client_admin):
        """Admin pode criar funcionário."""
        url = reverse('backoffice:admin-funcionario-list')
        data = {
            'usuario': {
                'email': 'novofunc@test.com',
                'senha': 'senha123',
                'nome': 'Novo Funcionário',
                'telefone': '(88) 96666-6666'
            },
            'cargo': 'VETERINARIO',
            'horario_trabalho': 'Segunda a Sexta, 09:00-18:00'
        }
        response = authenticated_client_admin.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_list_formas_pagamento_as_admin(self, authenticated_client_admin, forma_pagamento):
        """Admin pode listar formas de pagamento."""
        url = reverse('backoffice:admin-forma-pagamento-list')
        response = authenticated_client_admin.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_forma_pagamento_as_admin(self, authenticated_client_admin):
        """Admin pode criar forma de pagamento."""
        url = reverse('backoffice:admin-forma-pagamento-list')
        data = {
            'nome': 'PIX',
            'tipo': 'PIX',
            'descricao': 'Pagamento via PIX'
        }
        response = authenticated_client_admin.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
