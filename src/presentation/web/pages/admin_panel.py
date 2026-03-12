# Painel Administrativo com dados reais"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

API_URL = "http://localhost:8000"

def render():
    """Renderiza o painel administrativo"""
    
    # Verificar se é admin
    if not st.session_state.get('admin_logado'):
        st.error("❌ Acesso negado! Área restrita para administradores.")
        if st.button("← Voltar ao Login"):
            st.session_state.admin_logado = False
            st.rerun()
        return
    
    # CSS específico do admin
    st.markdown("""
    <style>
        .admin-header {
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .admin-logout {
            position: absolute;
            top: 1rem;
            right: 1rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            border-bottom: 4px solid #4361ee;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #4361ee;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        
        .metric-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header com botão de logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div class="admin-header">
            <h1 style="margin:0;">🔒 Painel Administrativo</h1>
            <p style="margin:0.5rem 0 0 0;">👤 {st.session_state.get('admin_user', 'Admin')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.admin_logado = False
            st.session_state.admin_user = None
            st.rerun()
    
    # Menu lateral simplificado
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/admin-settings-male.png", width=80)
        st.markdown("### 📊 Menu Admin")
        
        menu = st.radio(
            "Navegação",
            ["🏠 Visão Geral", "📋 Solicitações", "✅ Acessos", "📈 Estatísticas"],
            label_visibility="collapsed"
        )
    
    # Buscar dados da API
    auth = ("admin", "admin123")  # Temporário - depois usar credenciais reais
    
    try:
        if menu == "🏠 Visão Geral":
            render_visao_geral(auth)
        elif menu == "📋 Solicitações":
            render_solicitacoes(auth)
        elif menu == "✅ Acessos":
            render_acessos(auth)
        elif menu == "📈 Estatísticas":
            render_estatisticas(auth)
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

def render_visao_geral(auth):
    """Visão geral do admin"""
    
    # Buscar estatísticas
    response = requests.get(
        f"{API_URL}/api/admin/estatisticas",
        auth=auth,
        timeout=5
    )
    
    if response.status_code == 200:
        dados = response.json()
        if dados.get('sucesso'):
            stats = dados['estatisticas']
            
            # Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['total_solicitacoes']}</div>
                    <div class="stat-label">Solicitações</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['total_acessos']}</div>
                    <div class="stat-label">Acessos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['emails_unicos']}</div>
                    <div class="stat-label">E-mails</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['taxa_conversao']}%</div>
                    <div class="stat-label">Conversão</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráfico de solicitações por dia
            if stats.get('solicitacoes_por_dia'):
                st.subheader("📊 Solicitações por Dia")
                df = pd.DataFrame(stats['solicitacoes_por_dia'])
                fig = px.bar(df, x='dia', y='total', title="Últimos 7 dias")
                st.plotly_chart(fig, use_container_width=True)

def render_solicitacoes(auth):
    """Lista de solicitações"""
    
    st.subheader("📋 Solicitações de Chave")
    
    # Paginação
    if 'pagina_sol' not in st.session_state:
        st.session_state.pagina_sol = 1
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀ Anterior") and st.session_state.pagina_sol > 1:
            st.session_state.pagina_sol -= 1
            st.rerun()
    with col2:
        st.write(f"Página {st.session_state.pagina_sol}")
    with col3:
        if st.button("Próxima ▶"):
            st.session_state.pagina_sol += 1
            st.rerun()
    
    response = requests.get(
        f"{API_URL}/api/admin/solicitacoes",
        params={"pagina": st.session_state.pagina_sol, "limite": 50},
        auth=auth,
        timeout=5
    )
    
    if response.status_code == 200:
        dados = response.json()
        if dados.get('sucesso') and dados.get('dados'):
            df = pd.DataFrame(dados['dados'])
            st.dataframe(df, use_container_width=True)

def render_acessos(auth):
    """Lista de acessos"""
    
    st.subheader("✅ Acessos ao Dashboard")
    
    if 'pagina_ac' not in st.session_state:
        st.session_state.pagina_ac = 1
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀ Anterior", key="prev_ac") and st.session_state.pagina_ac > 1:
            st.session_state.pagina_ac -= 1
            st.rerun()
    with col2:
        st.write(f"Página {st.session_state.pagina_ac}")
    with col3:
        if st.button("Próxima ▶", key="next_ac"):
            st.session_state.pagina_ac += 1
            st.rerun()
    
    response = requests.get(
        f"{API_URL}/api/admin/acessos",
        params={"pagina": st.session_state.pagina_ac, "limite": 50},
        auth=auth,
        timeout=5
    )
    
    if response.status_code == 200:
        dados = response.json()
        if dados.get('sucesso') and dados.get('dados'):
            df = pd.DataFrame(dados['dados'])
            st.dataframe(df, use_container_width=True)

def render_estatisticas(auth):
    """Estatísticas detalhadas"""
    
    st.subheader("📈 Estatísticas Detalhadas")
    
    response = requests.get(
        f"{API_URL}/api/admin/estatisticas",
        auth=auth,
        timeout=5
    )
    
    if response.status_code == 200:
        dados = response.json()
        if dados.get('sucesso'):
            stats = dados['estatisticas']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Métricas")
                st.markdown(f"""
                <div class="metric-box">
                    <strong>Total Solicitações:</strong> {stats['total_solicitacoes']}<br>
                    <strong>Solicitações Hoje:</strong> {stats['solicitacoes_hoje']}<br>
                    <strong>Total Acessos:</strong> {stats['total_acessos']}<br>
                    <strong>Acessos Hoje:</strong> {stats['acessos_hoje']}<br>
                    <strong>E-mails Únicos:</strong> {stats['emails_unicos']}<br>
                    <strong>Taxa Conversão:</strong> {stats['taxa_conversao']}%
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📅 Últimos Dias")
                if stats.get('solicitacoes_por_dia'):
                    df = pd.DataFrame(stats['solicitacoes_por_dia'])
                    fig = px.line(df, x='dia', y='total', title="Evolução")
                    st.plotly_chart(fig, use_container_width=True)