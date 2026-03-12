#/bin/bash
# Mata todos os processos do projeto

echo "🔪 Matando todos os processos do projeto..."

# Matar uvicorn
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "uvicorn.*8001" 2>/dev/null

# Matar streamlit
pkill -f "streamlit.*8501" 2>/dev/null
pkill -f "streamlit.*8502" 2>/dev/null

# Matar qualquer coisa na porta
fuser -k 8000/tcp 2>/dev/null
fuser -k 8501/tcp 2>/dev/null
fuser -k 8502/tcp 2>/dev/null

echo "✅ Processos mortos!"
sleep 2

# Verificar
ss -tulpn | grep -E "8000|8501|8502" || echo "✅ Todas as portas livres!"