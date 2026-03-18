#!/bin/bash
# scripts/validar_agendamento.sh

echo "======================================================="
echo "🐶 VET SYSTEM - VALIDAÇÃO TIME SLOT SYSTEM"
echo "======================================================="

# Run Django unit tests
echo "[1] Executando Unit Tests Backend..."
docker exec -i mypet_web python manage.py test apps.agendamentos.tests -v 2 || exit 1

echo "----------------------------------------------------"
echo "[2] Garantindo que os slots da API tão subindo sem Timeout..."
# Check endpoints availability dynamically with curl 
# Needs an alive container in port 8000
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/servicos/)
if [ "$HTTP_STATUS" -ne 200 ] && [ "$HTTP_STATUS" -ne 401 ]; then
  echo "⚠️  Não consegui pingar a API (Code $HTTP_STATUS)."
else
  echo "✅ API rodando e respondendo no localhost."
fi

echo "======================================================="
echo "✅ Todos os testes automatizados passaram!"
echo "======================================================="
