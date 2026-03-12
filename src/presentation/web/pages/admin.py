"""Painel Administrativo simplificado"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000"

def render():
    """Renderiza o painel admin"""
    
    # Verificar autenticação admin
    if not st.session_state.get('admin_logado'):
        st.error("Acesso negado. Área restrita.")
        if st.button("← Voltar"):
            st.session_state.admin_logado = False
            st.rerun()
        return
    
    # Header com logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("🔒 Painel Administrativo")
        st.markdown(f"👤 {st.session_state.get('admin_user', 'Admin')}")
    with col2:
        if st.button("🚪 Sair"):
            st.session_state.admin_logado = False
            st.rerun()
    
    st.markdown("---")
    
    # Menu simples
    menu = st.radio(
        "Navegação",
        ["📊 Visão Geral", "📋 Solicitações", "✅ Acessos"],
        horizontal=True
    )
    
    # Credenciais (temporário - depois usar variáveis de ambiente)
    auth = ("admin", "admin123")
    
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
                    st.metric("Solicitações", stats['total_solicitacoes'], f"+{stats['solicitacoes_hoje']} hoje")
                with col2:
                    st.metric("Acessos", stats['total_acessos'], f"+{stats['acessos_hoje']} hoje")
                with col3:
                    st.metric("E-mails", stats['emails_unicos'])
                with col4:
                    st.metric("Conversão", f"{stats['taxa_conversao']}%")
                
                st.markdown("---")
                st.success("✅ Dados atualizados em tempo real")
            else:
                st.error(f"Erro: {dados.get('erro', 'Desconhecido')}")
        else:
            st.warning("API não disponível - mostrando dados de exemplo")
            # Dados de exemplo
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Solicitações", 150, "+12 hoje")
            with col2:
                st.metric("Acessos", 120, "+8 hoje")
            with col3:
                st.metric("E-mails", 45)
            with col4:
                st.metric("Conversão", "80%")
                
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
                
                # Download
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"solicitacoes_{datetime.now().strftime('%Y%m%d')}.csv"
                )
            else:
                st.info("Nenhuma solicitação encontrada")
        else:
            st.warning("API não disponível - mostrando dados de exemplo")
            # Dados de exemplo
            df_exemplo = pd.DataFrame([
                {"id": 1, "email": "usuario@exemplo.com", "data": "2026-03-11", "status": "ativa"},
                {"id": 2, "email": "outro@exemplo.com", "data": "2026-03-10", "status": "usada"}
            ])
            st.dataframe(df_exemplo)
            
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
            st.warning("API não disponível - mostrando dados de exemplo")
            # Dados de exemplo
            df_exemplo = pd.DataFrame([
                {"id": 1, "email": "usuario@exemplo.com", "data": "2026-03-11 10:30", "ip": "192.168.1.100"},
                {"id": 2, "email": "outro@exemplo.com", "data": "2026-03-11 09:15", "ip": "192.168.1.101"}
            ])
            st.dataframe(df_exemplo)
            
    except Exception as e:
        st.error(f"Erro: {e}")