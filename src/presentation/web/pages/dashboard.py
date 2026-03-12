# Dashboard principal simplificado"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

API_URL = "http://localhost:8000"

def render():
    """Renderiza o dashboard"""
    
    # Verificar autenticação
    if not st.session_state.get('authenticated'):
        st.warning("Você precisa fazer login primeiro")
        if st.button("← Voltar ao login"):
            st.session_state.authenticated = False
            st.rerun()
        return
    
    # Header com logout
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.title("📊 Dashboard")
    with col2:
        st.markdown(f"👤 {st.session_state.user_email}")
    with col3:
        if st.button("🚪 Sair"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Seleção de moedas (simples)
    st.subheader("🌍 Moedas")
    todas_moedas = ['USD', 'BRL', 'EUR', 'GBP', 'JPY', 'CNY']
    
    # Checkboxes em linha
    cols = st.columns(len(todas_moedas))
    selecionadas = []
    for i, moeda in enumerate(todas_moedas):
        with cols[i]:
            if st.checkbox(moeda, value=True):
                selecionadas.append(moeda)
    
    # Buscar dados
    if selecionadas:
        with st.spinner("🔄 Carregando dados..."):
            try:
                response = requests.get(
                    f"{API_URL}/api/investment/dados",
                    params={"moedas": ",".join(selecionadas)},
                    timeout=10
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    if dados.get('sucesso'):
                        # Cards com cotações
                        st.subheader("💰 Cotações")
                        cols = st.columns(len(selecionadas))
                        
                        for i, moeda in enumerate(selecionadas):
                            valor = dados['dados'].get(moeda, 0)
                            with cols[i]:
                                st.metric(
                                    label=f"USD/{moeda}",
                                    value=f"{valor:.4f}" if valor < 10 else f"{valor:.2f}"
                                )
                        
                        # Gráfico
                        st.subheader("📈 Visualização")
                        df = pd.DataFrame([
                            {"Moeda": k, "Taxa": v} 
                            for k, v in dados['dados'].items()
                        ])
                        
                        fig = px.bar(
                            df, 
                            x="Moeda", 
                            y="Taxa",
                            color="Moeda",
                            text_auto='.2f'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Bitcoin
                        if dados.get('bitcoin'):
                            st.subheader("₿ Bitcoin")
                            btc = dados['bitcoin']
                            st.info(f"**Preço:** {btc.get('formatted', 'N/A')} | **Fonte:** {btc.get('source', 'N/A')}")
                        
                        # Recomendações
                        st.subheader("💡 Recomendações")
                        rec_response = requests.get(
                            f"{API_URL}/api/investment/recomendacoes",
                            timeout=10
                        )
                        
                        if rec_response.status_code == 200:
                            rec_data = rec_response.json()
                            if rec_data.get('sucesso'):
                                for rec in rec_data.get('recomendacoes', []):
                                    with st.expander(f"📌 {rec['nome']}"):
                                        st.markdown(f"""
                                        **Prazo:** {rec['prazo']}  
                                        **Risco:** {rec['risco']}  
                                        **Razão:** {rec['razao']}
                                        """)
                    else:
                        st.error("Erro ao carregar dados")
                else:
                    st.error(f"Erro {response.status_code}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
    
    # Timestamp
    st.caption(f"🕐 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")