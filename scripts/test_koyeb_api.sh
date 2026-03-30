#!/usr/bin/env bash
# Script para testar a API no Koyeb

BACKEND_URL="https://electric-ki-investone-9623b27e.koyeb.app"

echo "🔍 Testando backend no Koyeb..."
echo "========================================="

# Teste 1: Health check
echo -e "\n1. Testando /api/health..."
curl -s -w "\nHTTP Status: %{http_code}\n" "${BACKEND_URL}/api/health" || echo "❌ Falha na conexão"

# Teste 2: Ping
echo -e "\n2. Testando /api/ping..."
curl -s -w "\nHTTP Status: %{http_code}\n" "${BACKEND_URL}/api/ping" || echo "❌ Falha na conexão"

# Teste 3: Solicitar chave
echo -e "\n3. Testando /api/solicitar-chave..."
curl -s -X POST "${BACKEND_URL}/api/solicitar-chave" \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@exemplo.com"}' \
  -w "\nHTTP Status: %{http_code}\n" || echo "❌ Falha na conexão"

echo -e "\n========================================="
echo "✅ Testes concluídos!"
