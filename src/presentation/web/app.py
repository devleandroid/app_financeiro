# Aplicação principal - Versão Simplificada"""
import sys
import os
from pathlib import Path
import streamlit as st

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Configurar URL da API
try:
    API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))
except:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

os.environ["API_URL"] = API_URL

from src.presentation.web.pages import render as render_pagina

# Configuração da página
st.set_page_config(
    page_title="InvestSmart",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    /* Estilos gerais */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #1e1e2f;
    }
    
    /* Botão primário */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #4361ee, #3f37c9);
        border: none;
        transition: transform 0.2s ease;
    }
    
    .stButton button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
    }
    
    /* Expandir (passo a passo) */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Métricas */
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    
    /* Remover menu lateral */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container principal */
    .main > div {
        padding: 1rem 2rem;
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
