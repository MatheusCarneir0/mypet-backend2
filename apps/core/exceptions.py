# apps/core/exceptions.py
"""
Exceções customizadas para a aplicação.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler customizado para exceções da API.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': response.data.get('detail', 'Erro na requisição'),
            'data': response.data
        }
        response.data = custom_response_data
    
    return response

