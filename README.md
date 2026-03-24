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
# cat > .env << 'EOF'
# Application
ENVIRONMENT=development
DEBUG=true
API_URL=http://localhost:8000

# Admin
ADMIN_USER=admin
ADMIN_PASS=sua_senha_forte

# API Keys
FIXER_API_KEY=SUA_CHAVE_DA_API

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/investsmart

# Email (for reports)
EMAIL_REMETENTE=seu_email@mail.com
EMAIL_SENHA=sua_chave_da_mensageria
SMTP_SERVIDOR=smtp.gmail.com
SMTP_PORTA=587

# EOF

# Verificar se o banco foi recriado
# Se o banco não existe, o sistema recria automaticamente
python -c "from src.infrastructure.database.unified_repository import admin_repo; print('Banco verificado')"

# Verificar se foi criado
ls -la acessos.db

# Testar o fluxo completo
# 1. Solicitar uma nova chave
curl -X POST http://localhost:8000/api/solicitar-chave \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@exemplo.com"}'

# 2. Verificar no banco
sqlite3 acessos.db "SELECT * FROM access_keys;"

# 3. Verificar no admin
curl -u admin:admin123 http://localhost:8000/api/admin/solicitacoes

# Execute localmente
# Em um terminal
./scripts/run_nix.sh backend

# Em outro terminal
./scripts/run_nix.sh frontend

# Opcional: painel admin
./scripts/run_nix.sh admin

# Matar todos os processos
./scripts/run_nix.sh kill-all

# Verificar ambiente
./scripts/run_nix.sh check