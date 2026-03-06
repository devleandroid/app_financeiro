# admin_simples.py - Versão sem plotly
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Admin - InvestSmart",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Painel Administrativo")
st.markdown("---")

# Configurações
API_URL = "http://localhost:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "sua_senha_forte"

# Login
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/admin-settings-male.png", width=80)
    st.markdown("### 🔐 Login Admin")
    
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar", use_container_width=True):
        st.session_state.auth = (username, password)

if 'auth' in st.session_state:
    auth = st.session_state.auth
    
    # Abas
    tab1, tab2 = st.tabs(["📊 Solicitações", "✅ Acessos"])
    
    with tab1:
        st.subheader("📧 Solicitações de Chave")
        
        response = requests.get(
            f"{API_URL}/api/admin/solicitacoes",
            auth=auth
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                st.dataframe(df, use_container_width=True)
                
                # Estatísticas básicas
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total", len(df))
                col2.metric("Usadas", len(df[df['usado'] == 1]) if 'usado' in df.columns else 0)
                col3.metric("Não usadas", len(df[df['usado'] == 0]) if 'usado' in df.columns else 0)
    
    with tab2:
        st.subheader("✅ Acessos ao Dashboard")
        
        response = requests.get(
            f"{API_URL}/api/admin/acessos",
            auth=auth
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                st.dataframe(df, use_container_width=True)

else:
    st.info("👈 Faça login na barra lateral")