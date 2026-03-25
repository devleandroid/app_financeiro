# 💰 InvestSmart

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Plataforma de análise de investimentos com dados em tempo real via Fixer.io.

---

## 🚀 Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=flat&logo=uvicorn&logoColor=white) |
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) / ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white) |
| **Infra** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) ![Koyeb](https://img.shields.io/badge/Koyeb-4285F4?style=flat&logo=koyeb&logoColor=white) ![NixOS](https://img.shields.io/badge/NixOS-5277C3?style=flat&logo=nixos&logoColor=white) |

---

## 📋 Pré-requisitos

- 🐍 **Python 3.11+**
- 🐳 **Docker** (opcional)
- 🔑 **Chave de API** do [Fixer.io](https://fixer.io) (gratuita)

---

## 🔧 Instalação Local

### 1️⃣ Clone o repositório

git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro

### 2️⃣ Crie um ambiente virtual

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

### 3️⃣ Instale as dependências

pip install -r requirements.txt

### 4️⃣ Configure as variáveis de ambiente

cp .env.example .env
### Edite .env com suas chaves

### Exemplo de .env:

Edite o arquivo .env com suas configurações:
### Application
ENVIRONMENT=development
DEBUG=true
API_URL=http://localhost:8000

### Admin
ADMIN_USER=admin
ADMIN_PASS=sua_senha_forte

### API Keys
FIXER_API_KEY=SUA_CHAVE_DA_API

### Database
DATABASE_URL=postgresql://user:pass@localhost:5432/investsmart

### Email (for reports)
EMAIL_REMETENTE=seu_email@mail.com
EMAIL_SENHA=sua_chave_da_mensageria
SMTP_SERVIDOR=smtp.gmail.com
SMTP_PORTA=587

### 5️⃣ Verifique o banco de dados
### Verificar se o banco foi recriado
python -c "from src.infrastructure.database.unified_repository import admin_repo; print('✅ Banco verificado')"

### Verificar se foi criado
ls -la acessos.db

### 6️⃣ Teste o fluxo completo
### 1. Solicitar uma nova chave
curl -X POST http://localhost:8000/api/solicitar-chave \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@exemplo.com"}'

### 2. Verificar no banco
sqlite3 acessos.db "SELECT * FROM access_keys;"

### 3. Verificar no admin
curl -u admin:admin123 http://localhost:8000/api/admin/solicitacoes

### 7️⃣ Execute localmente
 Serviço	Comando	Porta
 Backend	./scripts/run_nix.sh backend	8000
 Frontend	./scripts/run_nix.sh frontend	8501
 Admin	./scripts/run_nix.sh admin	8502


### Em um terminal
./scripts/run_nix.sh backend

### Em outro terminal
./scripts/run_nix.sh frontend

### Opcional: painel admin
./scripts/run_nix.sh admin

### 8️⃣ Comandos úteis
### Matar todos os processos
./scripts/run_nix.sh kill-all

### Verificar ambiente
./scripts/run_nix.sh check

### 🐳 Executar com Docker
docker-compose up -d

### Acesse:

Backend: http://localhost:8000

Frontend: http://localhost:8501

### ☁️ Deploy
## Koyeb

O projeto está configurado para deploy no Koyeb:

1.  Conecte seu repositório GitHub

2.  Configure as variáveis de ambiente

3.  Clique em "Deploy"

## Streamlit Cloud

O frontend pode ser publicado separadamente no Streamlit Cloud:

1. Acesse share.streamlit.io

2. Conecte seu repositório

3. Configure a variável API_URL apontando para o backend

### 📁 Estrutura do Projeto


# app_financeiro/
# ├── src/
# │   ├── domain/          # 📐 Regras de negócio
# │   ├── application/     # ⚙️ Casos de uso
# │   ├── infrastructure/  # 🗄️ Banco de dados, APIs externas
# │   └── presentation/    # 🖥️ FastAPI + Streamlit
# ├── tests/               # 🧪 Testes
# ├── scripts/             # 🔧 Scripts utilitários
# ├── nix/                 # ❄️ Configurações NixOS
# ├── docs/                # 📚 Documentação
# ├── Dockerfile           # 🐳 Container
# ├── docker-compose.yml   # 🐳 Orquestração
# ├── Makefile             # 🛠️ Comandos úteis
# └── requirements.txt     # 📦 Dependências

### 📝 Licença

### Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
### 👤 Autor

### Leandro Marques (DevLeandroid)

https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white
https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white

### ⭐ Se este projeto te ajudou, considere dar uma estrela no GitHub!
