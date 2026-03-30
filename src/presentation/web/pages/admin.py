import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def render():
    """Renderiza o painel administrativo"""
    
    # Verificar se está logado como admin
    if not st.session_state.get('admin_logado'):
        st.error("Acesso negado. Você não está logado como administrador.")
        if st.button("← Voltar ao login"):
            st.session_state.admin_logado = False
            st.rerun()
        return
    
    # HEADER COM BOTÃO DE SAIR
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("🔒 Painel Administrativo")
    with col2:
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            st.session_state.admin_logado = False
            st.session_state.admin_user = None
            st.success("✅ Logout realizado com sucesso!")
            st.rerun()
    
    st.markdown(f"Bem-vindo, administrador!")
    st.markdown("---")
    
    # Menu simplificado
    menu = st.radio(
        "Navegação",
        ["📊 Visão Geral", "📋 Solicitações", "✅ Acessos"],
        horizontal=True
    )
    
    # Credenciais para API (em produção, usar variáveis de ambiente)
    auth = (os.getenv("ADMIN_USER", "admin"), os.getenv("ADMIN_PASS", "admin123"))
    
    if menu == "📊 Visão Geral":
        render_visao_geral(auth)
    elif menu == "📋 Solicitações":
        render_solicitacoes(auth)
    elif menu == "✅ Acessos":
        render_acessos(auth)

def render_visao_geral(auth):
    """Visão geral com cards"""
    
    try:
        response = requests.get(
            f"{API_URL}/api/admin/estatisticas",
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso'):
                stats = dados['estatisticas']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Solicitações", stats['total_solicitacoes'])
                with col2:
                    st.metric("Total de Acessos", stats['total_acessos'])
                with col3:
                    st.metric("E-mails Únicos", stats['emails_unicos'])
                with col4:
                    st.metric("Taxa de Conversão", f"{stats['taxa_conversao']}%")
                
                st.markdown("---")
                st.success("✅ Dados atualizados em tempo real")
            else:
                st.error(f"Erro: {dados.get('erro', 'Desconhecido')}")
        else:
            st.warning("API não disponível")
                
    except Exception as e:
        st.error(f"Erro: {e}")

def render_solicitacoes(auth):
    """Lista de solicitações"""
    
    st.subheader("📋 Solicitações de Chave")
    
    try:
        response = requests.get(
            f"{API_URL}/api/admin/solicitacoes",
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"solicitacoes_{datetime.now().strftime('%Y%m%d')}.csv"
                )
            else:
                st.info("Nenhuma solicitação encontrada")
        else:
            st.warning("API não disponível")
            
    except Exception as e:
        st.error(f"Erro: {e}")

def render_acessos(auth):
    """Lista de acessos"""
    
    st.subheader("✅ Acessos ao Sistema")
    
    try:
        response = requests.get(
            f"{API_URL}/api/admin/acessos",
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum acesso registrado")
        else:
            st.warning("API não disponível")
            
    except Exception as e:
        st.error(f"Erro: {e}")