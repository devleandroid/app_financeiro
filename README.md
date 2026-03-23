# App de Recomendacoes Financeiras

Plataforma de analise de investimentos com dados em tempo real. Combina dados de cambio (Fixer.io), Bitcoin e indicadores economicos para gerar sugestoes de investimento de curto e longo prazo.

## Funcionalidades

- Busca taxas de cambio em tempo real (170+ moedas)
- Preco e tendencia do Bitcoin (CoinGecko + alternativas)
- Recomendacoes de investimento baseadas em logica de negocio
- Interface web com Streamlit
- Backend robusto com FastAPI
- Painel administrativo com autenticacao

## Tecnologias

- **Backend**: Python 3.12 + FastAPI + Uvicorn
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite (local) / PostgreSQL (Docker)
- **Infra**: Docker + Render / Streamlit Community Cloud

## Como Rodar Localmente

### Pre-requisitos

- Python 3.12 ou superior
- (Opcional) Chave de API gratuita do [Fixer.io](https://fixer.io/) - sem ela, dados simulados sao usados

### Passo a Passo

```bash
# 1. Clone o repositorio
git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro

# 2. Instale as dependencias
pip install -r requirements.txt

# 3. Configure as variaveis de ambiente
cp .env.example .env
# Edite .env com suas chaves (opcional)

# 4. Inicie o backend (terminal 1)
make run-backend

# 5. Inicie o frontend (terminal 2)
make run-frontend
```

O backend estara disponivel em `http://localhost:8000` (docs em `/docs`).
O frontend estara disponivel em `http://localhost:8501`.

### Com Docker

```bash
docker-compose up --build
```

## Deploy Gratuito

### Backend no Render.com

1. Crie uma conta gratuita em [render.com](https://render.com)
2. Clique em **New > Web Service**
3. Conecte seu repositorio GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.presentation.api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: `PYTHONPATH=.`, `ENVIRONMENT=production`
5. Clique em **Create Web Service** (plano Free)

Ou use o arquivo `render.yaml` incluido no projeto para deploy automatico via Blueprint.

### Frontend no Streamlit Community Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **New app**
3. Selecione o repositorio `devleandroid/app_financeiro`
4. Configure:
   - **Main file path**: `src/presentation/web/app.py`
   - **Advanced > Environment Variables**: `API_URL=https://SEU-BACKEND.onrender.com`
5. Clique em **Deploy**

### Variaveis de Ambiente para Deploy

| Variavel | Descricao | Obrigatoria |
|----------|-----------|-------------|
| `PYTHONPATH` | Definir como `.` | Sim (backend) |
| `ENVIRONMENT` | `production` | Sim (backend) |
| `API_URL` | URL publica do backend | Sim (frontend) |
| `CORS_EXTRA_ORIGINS` | URLs do frontend separadas por virgula | Sim (backend) |
| `FIXER_API_KEY` | Chave API do Fixer.io | Nao (usa dados simulados) |
| `ADMIN_USER` | Usuario admin | Nao (padrao: admin) |
| `ADMIN_PASS` | Senha admin | Nao (padrao: admin123) |

## Endpoints da API

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/` | Status do servidor |
| GET | `/docs` | Documentacao interativa (Swagger) |
| GET | `/api/health` | Health check |
| GET | `/api/ping` | Ping/pong |
| POST | `/api/solicitar-chave` | Solicitar chave de acesso |
| POST | `/api/validar-chave` | Validar chave de acesso |
| GET | `/api/investment/dados` | Dados de cambio e Bitcoin |
| GET | `/api/investment/recomendacoes` | Recomendacoes de investimento |
| GET | `/api/admin/solicitacoes` | Solicitacoes (protegido) |
| GET | `/api/admin/acessos` | Acessos (protegido) |
| GET | `/api/admin/estatisticas` | Estatisticas (protegido) |
