# /bin/bash
# scripts/run_nix.sh - Executa usando apenas Nix (sem pip)

export PYTHONPATH=.

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
    uvicorn src.presentation.api.main:app --reload --port 8000
    ;;
  frontend)
    echo "🎨 Iniciando frontend..."
    kill_port 8501
    streamlit run src/presentation/web/app.py --server.port 8501
    ;;
  admin)
    echo "🔒 Iniciando painel admin..."
    kill_port 8502
    streamlit run src/presentation/web/pages/admin_panel.py --server.port 8502
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
    python scripts/check_nix_env.py
    ;;
  *)
    echo "Uso: ./scripts/run_nix.sh [backend|frontend|admin|all|kill-all|check]"
    ;;
esac