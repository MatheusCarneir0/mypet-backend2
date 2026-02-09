"""
Testes para rotas de pets.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.pets
class TestPetEndpoints:
    """Testes para endpoints de pets."""
    
    def test_list_pets_as_cliente(self, authenticated_client_cliente, pet):
        """Cliente pode listar seus próprios pets."""
        url = reverse('pet-list')
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_pet(self, authenticated_client_cliente, cliente):
        """Cliente pode criar um pet."""
        url = reverse('pet-list')
        data = {
            'cliente': cliente.id,
            'nome': 'Miau',
            'especie': 'GATO',
            'raca': 'Persa',
            'idade': 2,
            'peso': 4.5,
            'observacoes': 'Gato tranquilo'
        }
        response = authenticated_client_cliente.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == 'Miau'
    
    def test_retrieve_pet(self, authenticated_client_cliente, pet):
        """Recuperar detalhes de um pet."""
        url = reverse('pet-detail', kwargs={'pk': pet.pk})
        response = authenticated_client_cliente.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == pet.nome
    
    def test_update_pet(self, authenticated_client_cliente, pet):
        """Atualizar dados de um pet."""
        url = reverse('pet-detail', kwargs={'pk': pet.pk})
        data = {
            'peso': 26.0,
            'observacoes': 'Peso atualizado'
        }
        response = authenticated_client_cliente.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['peso']) == 26.0
    
    def test_delete_pet(self, authenticated_client_cliente, pet):
        """Cliente pode deletar seu próprio pet."""
        url = reverse('pet-detail', kwargs={'pk': pet.pk})
        response = authenticated_client_cliente.delete(url)
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
    
    def test_list_pets_as_funcionario(self, authenticated_client_funcionario, pet):
        """Funcionário pode listar todos os pets."""
        url = reverse('pet-list')
        response = authenticated_client_funcionario.get(url)
        assert response.status_code == status.HTTP_200_OK
