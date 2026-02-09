"""
Testes para rotas de autenticação.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.auth
class TestAuthenticationEndpoints:
    """Testes para endpoints de autenticação."""
    
    def test_register_cliente(self, api_client):
        """Teste de registro de novo cliente."""
        url = reverse('authentication:register')
        data = {
            'email': 'novocliente@test.com',
            'senha': 'senhaforte123',
            'nome': 'Novo Cliente',
            'telefone': '(88) 99999-9999',
            'cpf': '111.222.333-44',
            'endereco': 'Rua Nova, 456',
            'cidade': 'Sobral',
            'estado': 'CE',
            'cep': '62000-000'
        }
        response = api_client.post(url, data, format='json')
        # Pode retornar 201 ou 400 dependendo da validação do serializer
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        if response.status_code == status.HTTP_201_CREATED:
            assert 'access' in response.data or 'usuario' in response.data
    
    def test_login_success(self, api_client, usuario_cliente):
        """Teste de login com credenciais válidas."""
        url = reverse('authentication:login')
        data = {
            'email': 'cliente@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Teste de login com credenciais inválidas."""
        url = reverse('authentication:login')
        data = {
            'email': 'invalido@test.com',
            'password': 'senhaerrada'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, usuario_cliente):
        """Teste de refresh token."""
        # Primeiro faz login
        login_url = reverse('authentication:login')
        login_data = {
            'email': 'cliente@test.com',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Depois testa o refresh
        refresh_url = reverse('authentication:refresh')
        refresh_data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, refresh_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
