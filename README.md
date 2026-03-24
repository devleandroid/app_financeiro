# 💰 InvestSmart

Plataforma de análise de investimentos com dados em tempo real via Fixer.io.

## 🚀 Tecnologias

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Infra**: Docker + Koyeb / NixOS

## 📋 Pré-requisitos

- Python 3.11+
- Docker (opcional)
- Chave de API do [Fixer.io](https://fixer.io)

## 🔧 Instalação Local

```bash
# Clone o repositório
git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves

# Execute localmente
make run-backend   # Terminal 1
make run-frontend  # Terminal 2