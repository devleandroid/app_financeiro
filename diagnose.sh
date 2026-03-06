#!/usr/bin/env bash

echo "🔍 DIAGNÓSTICO COMPLETO"
echo "========================"

# Verificar arquivo .env
echo -n "📁 Arquivo .env: "
if [ -f .env ]; then
    echo "✅ Existe"
    echo -n "   Chave API: "
    if grep -q "FIXER_API_KEY" .env; then
        key=$(grep "FIXER_API_KEY" .env | cut -d'=' -f2)
        echo "✅ Encontrada (${key:0:5}...${key: -5})"
    else
        echo "❌ Não encontrada"
    fi
else
    echo "❌ Não existe"
fi

echo ""

# Verificar se backend está rodando
echo -n "🚀 Backend: "
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Rodando"
else
    echo "❌ Parado"
fi

# Testar endpoints
echo ""
echo "📡 Testando endpoints:"
echo -n "   GET /: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/
echo ""

echo -n "   GET /health: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health
echo ""

echo -n "   GET /dados: "
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/dados-completos?moedas=BRL,EUR"
echo ""

# Testar Python
echo ""
echo "🐍 Testando imports Python:"
nix-shell --run "python -c 'import sys; print(f\"  Python: {sys.version.split()[0]}\")'"
nix-shell --run "python -c 'import requests; print(\"  requests: OK\")' 2>/dev/null || echo \"  requests: ❌\""
nix-shell --run "python -c 'import dotenv; print(\"  python-dotenv: OK\")' 2>/dev/null || echo \"  python-dotenv: ❌\""

echo ""
echo "📊 Teste completo!"
