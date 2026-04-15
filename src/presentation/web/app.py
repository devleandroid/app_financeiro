# Aplicação principal - Versão Responsiva
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

# CSS Responsivo para Mobile
st.markdown("""
<style>
    /* Reset e variáveis */
    :root {
        --primary: #4361ee;
        --primary-dark: #3f37c9;
        --success: #4cc9f0;
        --danger: #f72585;
        --warning: #f8961e;
        --dark: #1e1e2f;
        --light: #f8f9fa;
        --gray: #6c757d;
    }
    
    /* Estilos gerais */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Títulos responsivos */
    h1 {
        font-size: 1.8rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
    
    /* Cards responsivos */
    .currency-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    /* Botões */
    .stButton button {
        width: 100%;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Inputs */
    .stTextInput input {
        border-radius: 10px !important;
    }
    
    /* Remover elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ajuste do container principal */
    .main .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    
    /* ============================================
       ESTILOS ESPECÍFICOS PARA MOBILE
       ============================================ */
    
    /* Para telas pequenas (smartphones) */
    @media (max-width: 768px) {
        /* Títulos */
        h1 {
            font-size: 1.5rem !important;
            text-align: center !important;
        }
        
        /* Abas - estilo mais amigável para mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 auto !important;
            min-width: calc(33% - 8px) !important;
            padding: 0.5rem !important;
            font-size: 0.8rem !important;
            white-space: nowrap !important;
        }
        
        /* Cards de moedas em grid responsivo */
        div[data-testid="column"] {
            min-width: calc(50% - 1rem) !important;
            flex: 1 1 auto !important;
        }
        
        /* Métricas */
        div[data-testid="stMetric"] {
            padding: 0.5rem !important;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-size: 0.9rem !important;
        }
        
        /* Tabelas - scroll horizontal */
        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }
        
        /* Gráficos */
        .js-plotly-plot {
            height: 300px !important;
        }
    }
    
    /* Para telas muito pequenas */
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            min-width: calc(50% - 8px) !important;
            font-size: 0.7rem !important;
        }
        
        div[data-testid="column"] {
            min-width: 100% !important;
        }
        
        .currency-card .currency-value {
            font-size: 1.2rem !important;
        }
    }
    
    /* Cards com hover suave */
    .currency-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Indicadores de toque */
    .stButton button:active {
        transform: scale(0.98);
    }
    
    /* Animações suaves */
    * {
        transition: all 0.2s ease;
    }
    
    /* Scroll suave */
    html {
        scroll-behavior: smooth;
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
