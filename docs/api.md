# 📡 API Reference

## Base URL
https://seu-backend.onrender.com/api

## Endpoints

### Health Check

```http
GET /health

Response:
json

{
  "status": "ok",
  "timestamp": "2026-04-14T10:00:00"
}

Solicitar Chave
http

POST /solicitar-chave
Content-Type: application/json

{
  "email": "usuario@exemplo.com"
}

Response:
json

{
  "sucesso": true,
  "mensagem": "Chave enviada para usuario@exemplo.com! Válida por 4 horas."
}

Validar Chave
http

POST /validar-chave
Content-Type: application/json

{
  "chave": "ABCD1234"
}

Response:
json

{
  "sucesso": true,
  "mensagem": "✅ Acesso liberado! Chave válida por mais 3.5 horas.",
  "email": "usuario@exemplo.com"
}

Dados de Investimento
http

GET /investment/dados?moedas=BRL,USD,EUR

Response:
json

{
  "sucesso": true,
  "dados": {
    "BRL": 5.25,
    "USD": 1.0,
    "EUR": 0.92
  },
  "bitcoin": {
    "price": 65432.10,
    "change_24h": 2.5
  }
}

Recomendações
http

GET /investment/recomendacoes

Response:
json

{
  "sucesso": true,
  "recomendacoes": [
    {
      "nome": "🇧🇷 Ações de Exportação",
      "prazo": "Curto Prazo",
      "risco": "Médio",
      "razao": "Real forte favorece empresas exportadoras"
    }
  ]
}

Endpoints Administrativos (Protegidos)
http

# Requer autenticação Basic Auth (admin:senha)

GET /admin/estatisticas
GET /admin/solicitacoes
GET /admin/acessos

← Voltar
