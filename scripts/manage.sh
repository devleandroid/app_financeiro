#!/usr/bin/env bash

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKEND_PORT=8000
FRONTEND_PORT=8501

check_port() {
    local port=$1
    if ss -tulpn | grep -q ":$port"; then
        return 0 # porta em uso
    else
        return 1 # porta livre
    fi
}

kill_port() {
    local port=$1
    local pid=$(ss -tulpn | grep ":$port" | grep -oP 'pid=\K\d+' | head -1)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Matando processo $pid na porta $port${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

case $1 in
  backend)
    if check_port $BACKEND_PORT; then
        echo -e "${YELLOW}⚠️ Porta $BACKEND_PORT em uso. Tentando liberar...${NC}"
        kill_port $BACKEND_PORT
    fi
    
    echo -e "${GREEN}🚀 Iniciando backend FastAPI na porta $BACKEND_PORT...${NC}"
    echo -e "${BLUE}📡 URL: http://localhost:$BACKEND_PORT${NC}"
    echo -e "${BLUE}📚 Docs: http://localhost:$BACKEND_PORT/docs${NC}"
    echo ""
    
    nix-shell --run "uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT"
    ;;
    
  frontend)
    if check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}⚠️ Porta $FRONTEND_PORT em uso. Tentando liberar...${NC}"
        kill_port $FRONTEND_PORT
    fi
    
    echo -e "${GREEN}🎨 Iniciando frontend Streamlit na porta $FRONTEND_PORT...${NC}"
    echo -e "${BLUE}🌐 URL: http://localhost:$FRONTEND_PORT${NC}"
    echo ""
    
    nix-shell --run "streamlit run app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0"
    ;;
    
  both)
    echo -e "${GREEN}🚀 Iniciando backend e frontend...${NC}"
    
    # Liberar portas se necessário
    if check_port $BACKEND_PORT; then
        echo -e "${YELLOW}⚠️ Liberando porta $BACKEND_PORT...${NC}"
        kill_port $BACKEND_PORT
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}⚠️ Liberando porta $FRONTEND_PORT...${NC}"
        kill_port $FRONTEND_PORT
    fi
    
    # Inicia backend em background
    echo -e "${GREEN}📡 Backend: http://localhost:$BACKEND_PORT${NC}"
    nix-shell --run "uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT" &
    BACKEND_PID=$!
    
    # Espera um pouco para o backend iniciar
    sleep 2
    
    # Inicia frontend
    echo -e "${GREEN}🌐 Frontend: http://localhost:$FRONTEND_PORT${NC}"
    nix-shell --run "streamlit run app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0"
    
    # Quando frontend fechar, mata o backend
    echo -e "${YELLOW}Encerrando backend (PID: $BACKEND_PID)${NC}"
    kill $BACKEND_PID 2>/dev/null
    ;;
    
  kill-all)
    echo -e "${YELLOW}🔪 Matando todos os processos nas portas $BACKEND_PORT e $FRONTEND_PORT...${NC}"
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    echo -e "${GREEN}✅ Portas liberadas!${NC}"
    ;;
    
  status)
    echo -e "${BLUE}=== Status das Portas ===${NC}"
    
    if check_port $BACKEND_PORT; then
        pid=$(ss -tulpn | grep ":$BACKEND_PORT" | grep -oP 'pid=\K\d+' | head -1)
        cmd=$(ps -p $pid -o comm= 2>/dev/null)
        echo -e "${RED}❌ Porta $BACKEND_PORT: EM USO (PID: $pid - $cmd)${NC}"
    else
        echo -e "${GREEN}✅ Porta $BACKEND_PORT: LIVRE${NC}"
    fi
    
    if check_port $FRONTEND_PORT; then
        pid=$(ss -tulpn | grep ":$FRONTEND_PORT" | grep -oP 'pid=\K\d+' | head -1)
        cmd=$(ps -p $pid -o comm= 2>/dev/null)
        echo -e "${RED}❌ Porta $FRONTEND_PORT: EM USO (PID: $pid - $cmd)${NC}"
    else
        echo -e "${GREEN}✅ Porta $FRONTEND_PORT: LIVRE${NC}"
    fi
    ;;
    
  *)
    echo -e "${RED}❌ Comando não reconhecido${NC}"
    echo "Uso: ./scripts/manage.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  backend   - Inicia backend (porta $BACKEND_PORT)"
    echo "  frontend  - Inicia frontend (porta $FRONTEND_PORT)"
    echo "  both      - Inicia ambos"
    echo "  kill-all  - Mata todos os processos nas portas"
    echo "  status    - Verifica status das portas"
    ;;
esac
