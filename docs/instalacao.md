# 🔧 Instalação Local

## Pré-requisitos

- Python 3.11 ou superior
- Git
- (Opcional) Docker

## Passo a passo

### 1. Clone o repositório

```bash
git clone https://github.com/devleandroid/app_financeiro.git
cd app_financeiro

2. Crie um ambiente virtual
bash

python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

3. Instale as dependências
bash

pip install -r requirements.txt

4. Configure as variáveis de ambiente
bash

cp .env.example .env
# Edite .env com suas configurações

5. Execute o projeto
bash

# Terminal 1 - Backend
make run-backend

# Terminal 2 - Frontend
make run-frontend

6. Acesse o sistema

    Frontend: http://localhost:8501

    API: http://localhost:8000

    Documentação da API: http://localhost:8000/docs

🐳 Executar com Docker
bash

docker-compose up -d

🔧 Comandos úteis
Comando	Descrição
make run-backend	Inicia o backend
make run-frontend	Inicia o frontend
make run-admin	Inicia o painel admin
make test	Executa os testes
make clean	Limpa arquivos temporários
📁 Estrutura do Projeto
text

app_financeiro/
├── src/
│   ├── application/     # Casos de uso
│   ├── domain/          # Entidades e regras
│   ├── infrastructure/  # Banco, APIs externas
│   └── presentation/    # API e Frontend
├── tests/               # Testes
├── scripts/             # Scripts utilitários
├── Dockerfile
├── Makefile
└── requirements.txt

← Voltar
