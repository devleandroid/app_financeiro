"""Painel Administrativo simplificado"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

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
    
    # Credenciais (devem ser as mesmas do .env)
    # Em produção, use variáveis de ambiente
    auth = ("admin", "admin123")  # <-- Deve corresponder ao .env
    
    # Verificar conexão com a API
    try:
        health_check = requests.get(f"{API_URL}/api/health", timeout=2)
        if health_check.status_code != 200:
            st.error("❌ API não está respondendo. Verifique se o backend está rodando.")
            st.info("Execute: ./scripts/run_nix.sh backend")
            return
    except:
        st.error("❌ Não foi possível conectar à API")
        st.info("Execute: ./scripts/run_nix.sh backend")
        return
    
    if menu == "📊 Visão Geral":
        render_visao_geral(auth)
    elif menu == "📋 Solicitações":
        render_solicitacoes(auth)
    elif menu == "✅ Acessos":
        render_acessos(auth)

def render_visao_geral(auth):
    """Visão geral com cards - DADOS REAIS"""
    
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
                
                # Cards com dados REAIS
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total de Solicitações", 
                        stats['total_solicitacoes'], 
                        f"+{stats['solicitacoes_hoje']} hoje"
                    )
                with col2:
                    st.metric(
                        "Total de Acessos", 
                        stats['total_acessos'], 
                        f"+{stats['acessos_hoje']} hoje"
                    )
                with col3:
                    st.metric("E-mails Únicos", stats['emails_unicos'])
                with col4:
                    st.metric("Taxa de Conversão", f"{stats['taxa_conversao']}%")
                
                st.markdown("---")
                
                # Gráfico de solicitações por dia (se houver dados)
                if stats.get('solicitacoes_por_dia'):
                    st.subheader("📊 Solicitações por Dia (últimos 7 dias)")
                    df = pd.DataFrame(stats['solicitacoes_por_dia'])
                    
                    # Importar plotly apenas se necessário
                    import plotly.express as px
                    fig = px.bar(
                        df, 
                        x='dia', 
                        y='total',
                        title="Solicitações por Dia",
                        labels={'dia': 'Data', 'total': 'Número de Solicitações'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 Não há dados suficientes para gerar gráfico")
                
                # Últimas atividades
                st.subheader("🕐 Últimas Atividades")
                atividades_response = requests.get(
                    f"{API_URL}/api/admin/atividades?limite=5",
                    auth=auth,
                    timeout=5
                )
                
                if atividades_response.status_code == 200:
                    atv_data = atividades_response.json()
                    if atv_data.get('sucesso') and atv_data.get('atividades'):
                        for atv in atv_data['atividades']:
                            if atv['tipo'] == 'solicitacao':
                                st.markdown(f"📧 **{atv['email']}** solicitou chave em {atv['data'][:19]}")
                            else:
                                st.markdown(f"✅ **{atv['email']}** acessou o sistema em {atv['data'][:19]}")
                    else:
                        st.info("Nenhuma atividade recente")
                else:
                    st.warning("Não foi possível carregar atividades")
                    
            else:
                st.error(f"Erro na API: {dados.get('erro', 'Desconhecido')}")
        else:
            st.error(f"Erro de autenticação: {response.status_code}")
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

def render_solicitacoes(auth):
    """Lista de solicitações - DADOS REAIS"""
    
    st.subheader("📋 Solicitações de Chave")
    
    # Paginação
    if 'pagina_sol' not in st.session_state:
        st.session_state.pagina_sol = 1
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀ Anterior", key="prev_sol") and st.session_state.pagina_sol > 1:
            st.session_state.pagina_sol -= 1
            st.rerun()
    with col2:
        st.write(f"Página {st.session_state.pagina_sol}")
    with col3:
        if st.button("Próxima ▶", key="next_sol"):
            st.session_state.pagina_sol += 1
            st.rerun()
    
    try:
        response = requests.get(
            f"{API_URL}/api/admin/solicitacoes",
            params={"pagina": st.session_state.pagina_sol, "limite": 20},
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                
                # Formatar colunas para melhor visualização
                if 'data_solicitacao' in df.columns:
                    df['data_solicitacao'] = pd.to_datetime(df['data_solicitacao']).dt.strftime('%d/%m/%Y %H:%M')
                if 'data_expiracao' in df.columns:
                    df['data_expiracao'] = pd.to_datetime(df['data_expiracao']).dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(
                    df[['email', 'chave', 'data_solicitacao', 'status', 'ip']],
                    use_container_width=True,
                    column_config={
                        "email": "E-mail",
                        "chave": "Chave",
                        "data_solicitacao": "Solicitado em",
                        "status": "Status",
                        "ip": "IP"
                    }
                )
                
                st.caption(f"Total de registros nesta página: {len(df)}")
                
                # Download CSV
                if st.button("📥 Download CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Clique para baixar",
                        csv,
                        f"solicitacoes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv"
                    )
            else:
                st.info("Nenhuma solicitação encontrada")
        else:
            st.error(f"Erro ao buscar solicitações: {response.status_code}")
            
    except Exception as e:
        st.error(f"Erro: {e}")

def render_acessos(auth):
    """Lista de acessos - DADOS REAIS"""
    
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
    
    try:
        response = requests.get(
            f"{API_URL}/api/admin/acessos",
            params={"pagina": st.session_state.pagina_ac, "limite": 20},
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('sucesso') and dados.get('dados'):
                df = pd.DataFrame(dados['dados'])
                
                # Formatar datas
                if 'data_acesso' in df.columns:
                    df['data_acesso'] = pd.to_datetime(df['data_acesso']).dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(
                    df[['email', 'chave_utilizada', 'data_acesso', 'ip']],
                    use_container_width=True,
                    column_config={
                        "email": "E-mail",
                        "chave_utilizada": "Chave",
                        "data_acesso": "Data/Hora",
                        "ip": "IP"
                    }
                )
                
                # Estatísticas dos acessos
                st.markdown("---")
                st.subheader("📊 Estatísticas de Acesso")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total na página", len(df))
                with col2:
                    if 'email' in df.columns:
                        st.metric("E-mails únicos", df['email'].nunique())
                
                # Download
                if st.button("📥 Download CSV dos acessos"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Clique para baixar",
                        csv,
                        f"acessos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv"
                    )
            else:
                st.info("Nenhum acesso registrado")
        else:
            st.error(f"Erro ao buscar acessos: {response.status_code}")
            
    except Exception as e:
        st.error(f"Erro: {e}")