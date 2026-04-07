#!/usr/bin/env bash

case "$1" in
  frontend)
    echo "🎨 Iniciando frontend..."
    nix-shell --run "streamlit run src/presentation/web/app.py --server.port 8501"
    ;;
  backend)
    echo "🚀 Iniciando backend..."
    nix-shell --run "uvicorn src.presentation.api.main:app --reload --port 8000"
    ;;
  *)
    echo "Uso: ./scripts/run.sh [backend|frontend]"
    ;;
esac