# Aplicação principal - Versão Simplificada"""
import sys
import os
from pathlib import Path
import streamlit as st

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Forçar a leitura do Secret
try:
    api_url = st.secrets["API_URL"]
    st.success(f"✅ Secret carregado: {api_url}")
except Exception as e:
    st.error(f"❌ Secret não encontrado: {e}")
    api_url = "http://localhost:8000"

# Sobrescrever a variável de ambiente
os.environ["API_URL"] = api_url

from src.presentation.web.pages import render as render_pagina

# Configuração da página
st.set_page_config(
    page_title="InvestSmart",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS global mínimo
st.markdown("""
<style>
    /* Garantir que o menu lateral inicie recolhido */
    section[data-testid="stSidebar"] {
        width: 0 !important;
        opacity: 0;
        transition: width 0.3s ease, opacity 0.3s ease;
    }
    
    /* Quando o usuário passar o mouse, expande suavemente */
    section[data-testid="stSidebar"]:hover {
        width: 21rem !important;
        opacity: 1;
    }
    
    /* Botão de expandir/recolher personalizado */
    button[kind="header"] {
        background: transparent !important;
        border: none !important;
    }

    /* Remover elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fonte */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'admin_logado' not in st.session_state:
    st.session_state.admin_logado = False

# Renderizar página atual
render_pagina()