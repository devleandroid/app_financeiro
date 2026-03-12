# Aplicação principal - Versão Simplificada"""
import streamlit as st
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