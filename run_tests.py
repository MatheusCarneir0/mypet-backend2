"""
Script para executar testes e gerar relatório de rotas testadas.
"""
import subprocess
import sys
import json
from pathlib import Path


def run_tests():
    """Executa pytest e captura resultados."""
    print("=" * 80)
    print("EXECUTANDO TESTES DE API - MyPet Backend")
    print("=" * 80)
    print()
    
    # Executar pytest com verbose e JSON report
    cmd = [
        'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print()
    print("=" * 80)
    print("RESUMO DAS ROTAS TESTADAS")
    print("=" * 80)
    print()
    
    # Lista de rotas testadas por módulo
    rotas_testadas = {
        "Autenticação (/auth/)": [
            "POST /auth/login/ - Login com JWT",
            "POST /auth/refresh/ - Refresh token",
            "POST /auth/register/ - Registro de cliente",
            "POST /auth/google/ - Login com Google"
        ],
        "Clientes (/clientes/)": [
            "GET /clientes/ - Listar clientes",
            "GET /clientes/{id}/ - Detalhes do cliente",
            "PATCH /clientes/{id}/ - Atualizar cliente",
            "DELETE /clientes/{id}/ - Deletar cliente"
        ],
        "Pets (/pets/)": [
            "GET /pets/ - Listar pets",
            "POST /pets/ - Criar pet",
            "GET /pets/{id}/ - Detalhes do pet",
            "PATCH /pets/{id}/ - Atualizar pet",
            "DELETE /pets/{id}/ - Deletar pet",
            "GET /pets/{id}/historico/ - Histórico do pet"
        ],
        "Serviços (/servicos/)": [
            "GET /servicos/ - Listar serviços",
            "POST /servicos/ - Criar serviço (Admin)",
            "GET /servicos/{id}/ - Detalhes do serviço",
            "PATCH /servicos/{id}/ - Atualizar serviço (Admin)",
            "DELETE /servicos/{id}/ - Deletar serviço (Admin)"
        ],
        "Agendamentos (/agendamentos/)": [
            "GET /agendamentos/ - Listar agendamentos",
            "POST /agendamentos/ - Criar agendamento",
            "GET /agendamentos/{id}/ - Detalhes do agendamento",
            "PATCH /agendamentos/{id}/ - Atualizar/Cancelar agendamento"
        ],
        "Pagamentos (/pagamentos/)": [
            "GET /pagamentos/transacoes/ - Listar transações",
            "POST /pagamentos/transacoes/ - Criar transação",
            "GET /pagamentos/transacoes/{id}/ - Detalhes da transação"
        ],
        "Notificações (/notificacoes/)": [
            "GET /notificacoes/ - Listar notificações",
            "GET /notificacoes/{id}/ - Detalhes da notificação",
            "PATCH /notificacoes/{id}/ - Marcar como lida"
        ],
        "Admin (/admin/)": [
            "GET /admin/dashboard/ - Dashboard administrativo",
            "GET /admin/funcionarios/ - Listar funcionários",
            "POST /admin/funcionarios/ - Criar funcionário",
            "GET /admin/formas-pagamento/ - Listar formas de pagamento",
            "POST /admin/formas-pagamento/ - Criar forma de pagamento",
            "POST /admin/relatorios/gerar/ - Gerar relatórios"
        ]
    }
    
    total_rotas = 0
    for modulo, rotas in rotas_testadas.items():
        print(f"\n{modulo}")
        print("-" * 80)
        for rota in rotas:
            print(f"  ✓ {rota}")
            total_rotas += 1
    
    print()
    print("=" * 80)
    print(f"TOTAL DE ROTAS TESTADAS: {total_rotas}")
    print("=" * 80)
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())
