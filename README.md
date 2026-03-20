# App de Recomendações Financeiras 💰

Este projeto combina dados de câmbio (Fixer.io), Bitcoin e indicadores econômicos para gerar 5 sugestões de investimento de curto e longo prazo.

## 🚀 Funcionalidades

-   Busca taxas de câmbio em tempo real (170+ moedas).
-   Simula dados de preço e tendência do Bitcoin.
-   Gera recomendações de investimento baseadas em uma lógica de negócio (customizável).
-   Interface web simples com Streamlit.
-   Backend robusto com FastAPI.

# Plataforma de análise de investimentos com dados em tempo real.# Plataforma de análise de investimentos com dados em tempo real.
## 🛠️ Tecnologias Utilizadas

-   Python 3.12+
-   FastAPI
-   Streamlit
-   Pandas
-   Requests

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit + Plotly
- **Database**: PostgreSQL
- **Infra**: Docker + Koyeb

## ⚙️ Como Configurar e Executar

## 📋 Pré-requisitos

- Python 3.12 ou superior instalado.
- Uma chave de API gratuita do [Fixer.io](https://fixer.io/).

### Passos

# Clone o repositório
git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro### Passos

# Clone o repositório
git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves

# Execute localmente
make run-backend
make run-frontend