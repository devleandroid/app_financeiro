#!/usr/bin/env bash
# scripts/run_nix.sh - Executa usando apenas Nix (sem pip)

export PYTHONPATH=.

# Caminho para o shell.nix (agora na pasta nix/)
SHELL_NIX_PATH="$(dirname "$0")/../nix/shell.nix"

kill_port() {
    local port=$1
    echo "🔪 Liberando porta $port..."
    fuser -k $port/tcp 2>/dev/null
    sleep 1
}

case $1 in
  backend)
    echo "🚀 Iniciando backend..."
    kill_port 8000
    nix-shell "$SHELL_NIX_PATH" --run "uvicorn src.presentation.api.main:app --reload --port 8000"
    ;;
  frontend)
    echo "🎨 Iniciando frontend..."
    kill_port 8501
    nix-shell "$SHELL_NIX_PATH" --run "streamlit run src/presentation/web/app.py --server.port 8501"
    ;;
  admin)
    echo "🔒 Iniciando painel admin..."
    kill_port 8502
    nix-shell "$SHELL_NIX_PATH" --run "streamlit run src/presentation/web/pages/admin.py --server.port 8502"
    ;;
  all)
    echo "🚀 Iniciando todos os serviços..."
    $0 backend &
    sleep 3
    $0 frontend &
    sleep 2
    $0 admin &
    ;;
  kill-all)
    echo "🔪 Matando todas as portas..."
    kill_port 8000
    kill_port 8501
    kill_port 8502
    echo "✅ Portas liberadas!"
    ;;
  check)
    echo "🔍 Verificando ambiente..."
    nix-shell "$SHELL_NIX_PATH" --run "python scripts/check_env.py"
    ;;
  *)
    echo "Uso: ./scripts/run_nix.sh [backend|frontend|admin|all|kill-all|check]"
    ;;
esac