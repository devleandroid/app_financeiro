#!/usr/bin/env bash

# Cores para output
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# NC='\033[0m' # No Color

# case $1 in
#   backend)
#     echo -e "${GREEN}🚀 Iniciando backend FastAPI...${NC}"
#     nix-shell --run "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
#     ;;
    
#   frontend)
#     echo -e "${GREEN}🎨 Iniciando frontend Streamlit...${NC}"
#     nix-shell --run "streamlit run app.py --server.port 8501"
#     ;;
    
#   both)
#     echo -e "${GREEN}🚀 Iniciando backend e frontend...${NC}"
#     # Inicia backend em background
#     nix-shell --run "uvicorn main:app --reload --host 0.0.0.0 --port 8000" &
#     BACKEND_PID=$!
#     echo -e "${YELLOW}Backend PID: $BACKEND_PID${NC}"
    
#     # Inicia frontend
#     nix-shell --run "streamlit run app.py --server.port 8501"
    
#     # Quando frontend fechar, mata o backend
#     kill $BACKEND_PID
#     ;;
    
#   shell)
#     echo -e "${GREEN}🐚 Entrando no shell Nix...${NC}"
#     nix-shell
#     ;;
    
#   test)
#     echo -e "${GREEN}🧪 Testando ambiente...${NC}"
#     nix-shell --run "python -c 'import numpy as np; import pandas as pd; print(\"✅ NumPy versão:\", np.__version__); print(\"✅ Pandas versão:\", pd.__version__)'"
#     ;;
    
#   install)
#     echo -e "${GREEN}📦 Instalando novo pacote Python...${NC}"
#     if [ -z "$2" ]; then
#       echo -e "${RED}❌ Especifique o pacote para instalar${NC}"
#       exit 1
#     fi
#     nix-shell --run "pip install $2"
#     ;;
    
#   *)
#     echo -e "${RED}❌ Comando não reconhecido${NC}"
#     echo "Uso: ./scripts/start.sh [comando]"
#     echo ""
#     echo "Comandos disponíveis:"
#     echo "  backend   - Inicia apenas o backend FastAPI"
#     echo "  frontend  - Inicia apenas o frontend Streamlit"
#     echo "  both      - Inicia ambos (recomendado)"
#     echo "  shell     - Entra no shell Nix interativo"
#     echo "  test      - Testa se as bibliotecas estão funcionando"
#     echo "  install   - Instala novo pacote Python (ex: ./start.sh install requests)"
#     ;;
# esac

check_backend() {
    for i in {1..10}; do
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo "✅ Backend está rodando"
            return 0
        fi
        echo "⏳ Aguardando backend... ($i/10)"
        sleep 1
    done
    echo "❌ Backend não respondeu"
    return 1
}

case $1 in
  backend)
    echo "🚀 Iniciando backend..."
    nix-shell --run "python main.py"
    ;;
    
  frontend)
    echo "🎨 Iniciando frontend..."
    echo "⏳ Aguardando backend ficar pronto..."
    if check_backend; then
        nix-shell --run "streamlit run app.py --server.port 8501"
    else
        echo "❌ Frontend não pode iniciar sem backend"
        exit 1
    fi
    ;;
    
  both)
    echo "🚀 Iniciando backend e frontend..."
    # Inicia backend em background
    nix-shell --run "python main.py" &
    BACKEND_PID=$!
    
    # Aguarda backend
    if check_backend; then
        # Inicia frontend
        nix-shell --run "streamlit run app.py --server.port 8501"
        # Quando frontend fechar, mata backend
        kill $BACKEND_PID 2>/dev/null
    else
        echo "❌ Falha ao iniciar backend"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    ;;
    
  *)
    echo "Uso: ./scripts/start.sh [backend|frontend|both]"
    ;;
esac
