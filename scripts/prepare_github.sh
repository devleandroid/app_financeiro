#!/usr/bin/env bash
# Script para preparar o projeto para o GitHub (NÃO remove arquivos locais)

echo "🧹 Preparando projeto para o GitHub..."
echo "========================================="

# 1. Verificar arquivos sensíveis que NÃO devem ser commitados
echo -e "\n🔍 Verificando arquivos sensíveis..."

SENSITIVE_FILES=(
    ".env"
    ".streamlit/secrets.toml"
    "acessos.db"
    "acessos.db.backup"
    "*.log"
    "app_financeiro.tar.gz"
    "ssh-key-*.key"
    "ssh-key-*.key.pub"
    "*.pyc"
    "__pycache__/"
    ".pytest_cache/"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if ls $file 2>/dev/null | head -1; then
        echo "   ⚠️  Sensitive file found: $file (will be ignored)"
    fi
done

# 2. Verificar .gitignore
echo -e "\n📁 Verificando .gitignore..."
if [ ! -f .gitignore ]; then
    
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
.pytest_cache/
.coverage
htmlcov/

# Database
*.db
*.sqlite3
*.sqlite
*.db-journal

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Project specific
result
*.bak
*.backup
acessos.db.backup
app_financeiro.tar.gz

# SSH Keys
ssh-key-*.key
ssh-key-*.key.pub

# Secrets
.streamlit/secrets.toml
.env
GITEOF
    echo "   ✅ .gitignore criado"
else
    echo "   ✅ .gitignore já existe"
fi

# 3. Verificar .env.example
echo -e "\n📁 Verificando .env.example..."
if [ ! -f .env.example ]; then
    
# Configurações da Aplicação
ENVIRONMENT=development
DEBUG=true
API_URL=http://localhost:8000

# Admin
ADMIN_USER=admin
ADMIN_PASS=change_this_password

# APIs Externas
FIXER_API_KEY=your_fixer_api_key_here

# Email (para relatórios)
EMAIL_REMETENTE=your_email@gmail.com
EMAIL_SENHA=your_app_password
SMTP_SERVIDOR=smtp.gmail.com
SMTP_PORTA=587
ENVEOF
    echo "   ✅ .env.example criado"
else
    echo "   ✅ .env.example já existe"
fi

# 4. Verificar se requirements.txt existe
echo -e "\n📁 Verificando requirements.txt..."
if [ ! -f requirements.txt ]; then
    echo "   ❌ requirements.txt não encontrado!"
else
    echo "   ✅ requirements.txt encontrado"
fi

# 5. Verificar Dockerfile
echo -e "\n📁 Verificando Dockerfile..."
if [ ! -f Dockerfile ]; then
    echo "   ❌ Dockerfile não encontrado!"
else
    echo "   ✅ Dockerfile encontrado"
fi

# 6. Verificar Makefile
echo -e "\n📁 Verificando Makefile..."
if [ ! -f Makefile ]; then
    echo "   ❌ Makefile não encontrado!"
else
    echo "   ✅ Makefile encontrado"
fi

# 7. Verificar koyeb.yaml
echo -e "\n📁 Verificando koyeb.yaml..."
if [ ! -f koyeb.yaml ]; then
    echo "   ⚠️ koyeb.yaml não encontrado (opcional)"
else
    echo "   ✅ koyeb.yaml encontrado"
fi

# 8. Listar o que será commitado
echo -e "\n📊 Arquivos que serão commitados:"
echo "========================================="
git status --short 2>/dev/null || echo "   (git não inicializado)"

echo -e "\n✅ Preparação concluída!"
echo ""
echo "Para commitar:"
echo "   git add ."
echo "   git status"
echo "   git commit -m 'feat: versão estável do InvestSmart'"
echo "   git push origin main"