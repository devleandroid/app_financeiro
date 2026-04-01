# 💰 InvestSmart

Plataforma de análise de investimentos com dados em tempo real via Fixer.io.

## 🚀 Tecnologias

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite (dev) / PostgreSQL (prod)
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
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves

# Execute localmente
make run-backend   # Terminal 1
make run-frontend  # Terminal 2

🐳 Executar com Docker

docker-compose up -d

☁️ Deploy

Koyeb

O projeto está configurado para deploy no Koyeb:

    Conecte seu repositório GitHub

    Configure as variáveis de ambiente

    Clique em "Deploy"

Streamlit Cloud

O frontend pode ser publicado separadamente no Streamlit Cloud:

    Acesse share.streamlit.io

    Conecte seu repositório

    Configure API_URL apontando para o backend


📝 Licença

MIT
👤 Autor

Leandro Marques (DevLeandroid)