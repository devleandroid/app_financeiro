#!/usr/bin/env bash
# run.sh - Script para rodar tudo no NixOS

case $1 in
  backend)
    echo "🚀 Iniciando backend..."
    nix-shell --run "python main.py"
    ;;
  frontend)
    echo "🎨 Iniciando frontend..."
    nix-shell --run "streamlit run app.py"
    ;;
  admin)
    echo "🔒 Iniciando admin..."
    nix-shell --run "streamlit run admin.py --server.port 8502"
    ;;
  relatorio)
    echo "📊 Enviando relatório..."
    nix-shell --run "python scripts/relatorio_email.py"
    ;;
  install)
    echo "📦 Instalando dependências..."
    nix-shell --run "pip install -r requirements.txt"
    ;;
  *)
    echo "Uso: ./run.sh [backend|frontend|admin|relatorio|install]"
    ;;
esac