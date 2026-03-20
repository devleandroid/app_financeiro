#/bin/bash
# scripts/remove_large_file_nixos.sh - Remove arquivo grande do histórico (NixOS)

echo "🧹 Removendo arquivo grande do histórico Git..."
echo "================================================"

# 1. Verificar se estamos no nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "❌ Este script deve ser executado dentro do nix-shell"
    echo "   Execute primeiro: nix-shell"
    exit 1
fi

# 2. Verificar se git-filter-repo está disponível
if ! command -v git-filter-repo &> /dev/null; then
    echo "⚠️ git-filter-repo não encontrado. Usando git filter-branch..."
    USE_FILTER_BRANCH=1
else
    USE_FILTER_BRANCH=0
fi

# 3. Fazer backup (opcional)
echo "📦 Criando backup do repositório..."
cd ..
cp -r app_financeiro app_financeiro_backup_$(date +%Y%m%d)
cd app_financeiro

# 4. Remover o arquivo
if [ $USE_FILTER_BRANCH -eq 0 ]; then
    echo "🔧 Usando git-filter-repo..."
    git filter-repo --path Miniconda3-latest-Linux-x86_64.sh --invert-paths --force
else
    echo "🔧 Usando git filter-branch..."
    git filter-branch --force --index-filter \
      "git rm --cached --ignore-unmatch Miniconda3-latest-Linux-x86_64.sh" \
      --prune-empty --tag-name-filter cat -- --all
      
    # Limpar referências
    git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
    git reflog expire --expire=now --all
    git gc --aggressive --prune=now
fi

# 5. Verificar se removeu
echo -e "\n🔍 Verificando se arquivo foi removido:"
git rev-list --objects --all | grep Miniconda || echo "✅ Arquivo removido com sucesso!"

# 6. Adicionar ao .gitignore
echo "Miniconda*.sh" >> .gitignore
git add .gitignore
git commit -m "chore: atualiza .gitignore"

# 7. Push
echo -e "\n📤 Enviando para GitHub..."
git remote add origin https://github.com/devleandroid/app_financeiro.git 2>/dev/null
git push origin main --force

echo -e "\n🎯 Limpeza concluída!"