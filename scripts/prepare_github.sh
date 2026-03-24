#!/usr/bin/env bash
# Script para preparar o projeto para o GitHub

echo "🧹 Preparando projeto para o GitHub..."
echo "========================================="

# 1. Remover arquivos de banco de dados
echo -e "\n📁 Removendo bancos de dados..."
rm -f acessos.db
rm -f acessos.db.backup*
rm -f *.sqlite3
echo "   ✅ Bancos de dados removidos"

# 2. Remover arquivos de ambiente e senhas
echo -e "\n📁 Removendo arquivos de ambiente..."
rm -f .env
rm -f .streamlit/secrets.toml 2>/dev/null
echo "   ✅ Arquivos .env removidos"

# 3. Remover arquivos temporários e de log
echo -e "\n📁 Removendo arquivos temporários..."
rm -f *.log
rm -f *.bak
rm -f *.backup
rm -f *.pyc
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/
echo "   ✅ Temporários removidos"

# 4. Remover arquivos de teste/desenvolvimento
echo -e "\n📁 Removendo arquivos de desenvolvimento..."
rm -f test_*.py
rm -f check_packages.py
rm -f diagnostico.py
rm -f criar_banco.py
rm -f corrigir_banco.py
rm -f dados_validados.json
rm -f taxas_referencia.json
rm -f @laura @laura.pub
rm -f Miniconda*.sh
echo "   ✅ Arquivos de teste removidos"

# 5. Remover scripts duplicados/antigos
echo -e "\n📁 Limpando scripts..."
rm -f scripts/run_*.sh 2>/dev/null
rm -f scripts/kill_all.sh 2>/dev/null
rm -f scripts/manage.sh 2>/dev/null
rm -f scripts/start.sh 2>/dev/null
echo "   ✅ Scripts antigos removidos"

# 6. Limpar diretórios de backup
echo -e "\n📁 Removendo backups..."
rm -rf .archive/
rm -rf src/presentation/web/pages/backup/
echo "   ✅ Backups removidos"

# 7. Remover __pycache__ de todos os diretórios
echo -e "\n📁 Removendo caches Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Caches removidos"

# 8. Criar .env.example se não existir
echo -e "\n📁 Verificando .env.example..."
if [ ! -f .env.example ]; then
    cat > .env.example << 'ENVEOF'
# Configurações da Aplicação
ENVIRONMENT=development
DEBUG=true
API_URL=http://localhost:8000

# Admin
ADMIN_USER=admin
ADMIN_PASS=change_this_password

# APIs Externas
FIXER_API_KEY=your_fixer_api_key_here

# Email (opcional - para relatórios)
EMAIL_REMETENTE=your_email@gmail.com
EMAIL_SENHA=your_app_password
SMTP_SERVIDOR=smtp.gmail.com
SMTP_PORTA=587
ENVEOF
    echo "   ✅ .env.example criado"
else
    echo "   ✅ .env.example já existe"
fi

# 9. Criar .gitignore se não existir
echo -e "\n📁 Verificando .gitignore..."
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'GITEOF'
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

# Secrets
.streamlit/secrets.toml
GITEOF
    echo "   ✅ .gitignore criado"
else
    echo "   ✅ .gitignore já existe"
fi

# 10. Verificar estrutura final
echo -e "\n📊 Estrutura final do projeto:"
tree -L 3 -I 'venv|__pycache__|*.pyc|.git|result' --dirsfirst 2>/dev/null || find . -maxdepth 3 -type d | head -30

echo -e "\n📊 Resumo da limpeza:"
echo "========================================="
echo "✅ Arquivos temporários removidos"
echo "✅ Bancos de dados removidos"
echo "✅ Arquivos .env removidos"
echo "✅ .env.example criado"
echo "✅ .gitignore configurado"
echo "========================================="
echo -e "\n🎯 Projeto pronto para o GitHub!"
echo "Para commitar:"
echo "  git add ."
echo "  git commit -m 'Initial commit: projeto organizado'"
echo "  git push origin main"
