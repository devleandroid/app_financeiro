# Dashboard principal simplificado"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

API_URL = "http://localhost:8000"

def formatar_taxa(moeda: str, valor: float) -> str:
    """Formata a taxa de câmbio com 2 casas decimais para todas as moedas"""
    if moeda == 'USD':
        return f"$ 1,00"
    elif moeda == 'JPY':
        return f"¥ {valor:,.0f}"  # Iene não usa decimais
    else:
        # TODAS as outras moedas com 2 casas decimais
        if moeda == 'BRL':
            return f"R$ {valor:.2f}"
        elif moeda == 'EUR':
            return f"€ {valor:.2f}"
        elif moeda == 'GBP':
            return f"£ {valor:.2f}"
        elif moeda == 'CNY':
            return f"¥ {valor:.2f}"
        else:
            return f"{valor:.2f}"

def get_nome_moeda(moeda: str) -> str:
    """Retorna o nome completo da moeda"""
    nomes = {
        'USD': 'Dólar Americano',
        'BRL': 'Real Brasileiro',
        'EUR': 'Euro',
        'GBP': 'Libra Esterlina',
        'JPY': 'Iene Japonês',
        'CNY': 'Yuan Chinês',
        'CAD': 'Dólar Canadense',
        'AUD': 'Dólar Australiano',
        'CHF': 'Franco Suíço'
    }
    return nomes.get(moeda, moeda)

def get_bandeira(moeda: str) -> str:
    """Retorna a bandeira do país"""
    bandeiras = {
        'USD': '🇺🇸',
        'BRL': '🇧🇷',
        'EUR': '🇪🇺',
        'GBP': '🇬🇧',
        'JPY': '🇯🇵',
        'CNY': '🇨🇳',
        'CAD': '🇨🇦',
        'AUD': '🇦🇺',
        'CHF': '🇨🇭'
    }
    return bandeiras.get(moeda, '🌍')

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
        st.title("📊 Dashboard de Câmbio")
    with col2:
        st.markdown(f"👤 {st.session_state.user_email}")
    with col3:
        if st.button("🚪 Sair"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # CSS personalizado
    st.markdown("""
    <style>
        .currency-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 5px solid #4361ee;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .currency-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(67, 97, 238, 0.2);
        }
        .currency-card.usd {
            border-left-color: #f72585;
            background: linear-gradient(135deg, #fff5f5, #ffffff);
        }
        .currency-pair {
            font-size: 1.2rem;
            font-weight: 600;
            color: #4361ee;
        }
        .currency-pair.usd {
            color: #f72585;
        }
        .currency-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        .currency-name {
            color: #666;
            font-size: 0.9rem;
        }
        .info-text {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #1976d2;
        }
        .usd-highlight {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #f72585;
            margin: 1rem 0;
        }
        .note {
            font-size: 0.8rem;
            color: #666;
            text-align: center;
            margin-top: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Explicação
    st.markdown("""
    <div class="info-text">
        <strong>📌 Entendendo as cotações:</strong><br>
        • <strong>USD (Dólar Americano)</strong> é a moeda base utilizada em todos os mercados internacionais.<br>
        • As cotações mostram <strong>quantos reais (R$)</strong> ou a moeda local equivalem a <strong>1 Dólar Americano (USD)</strong>.<br>
        • Exemplo: USD/BRL = 5,25 significa que US$ 1,00 vale R$ 5,25.<br>
        • <strong>Nota:</strong> Todas as moedas são mostradas com 2 casas decimais (exceto Iene Japonês).
    </div>
    """, unsafe_allow_html=True)
    
    # Seleção de moedas
    st.subheader("🌍 Moedas Disponíveis")
    
    # USD sempre incluso
    st.markdown("""
    <div class="usd-highlight">
        <strong>🇺🇸 USD - Dólar Americano</strong> (moeda base - sempre incluída)
    </div>
    """, unsafe_allow_html=True)
    
    todas_moedas = ['BRL', 'EUR', 'GBP', 'JPY', 'CNY', 'CAD', 'AUD', 'CHF']
    
    # Layout em grid para checkboxes
    cols = st.columns(4)
    selecionadas = ['USD']  # USD sempre incluso
    
    for i, moeda in enumerate(todas_moedas):
        with cols[i % 4]:
            bandeira = get_bandeira(moeda)
            nome = get_nome_moeda(moeda)
            if st.checkbox(f"{bandeira} {moeda} - {nome}", value=moeda in ['BRL', 'EUR', 'GBP'], key=f"cb_{moeda}"):
                selecionadas.append(moeda)
    
    # Buscar dados
    if len(selecionadas) > 1:
        with st.spinner("🔄 Carregando dados do Fixer.io..."):
            try:
                response = requests.get(
                    f"{API_URL}/api/investment/dados",
                    params={"moedas": ",".join(selecionadas)},
                    timeout=10
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    if dados.get('sucesso'):
                        rates = dados['dados']
                        
                        st.markdown("---")
                        st.subheader("💰 Cotações em Tempo Real")
                        st.caption(f"Base: 1 USD (Dólar Americano) • Data: {dados.get('data', datetime.now().strftime('%Y-%m-%d'))}")
                        
                        # Cards - USD primeiro
                        st.markdown("### 🇺🇸 Moeda Base")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.markdown(f"""
                            <div class="currency-card usd">
                                <div style="font-size: 2.5rem;">🇺🇸</div>
                                <div class="currency-pair usd">USD/USD</div>
                                <div class="currency-value">$ 1,00</div>
                                <div class="currency-name">Dólar Americano (Moeda Base)</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("### 💱 Moedas Cotadas")
                        moedas_cotadas = [m for m in selecionadas if m != 'USD']
                        cols = st.columns(len(moedas_cotadas))
                        
                        for i, moeda in enumerate(moedas_cotadas):
                            with cols[i]:
                                valor = rates.get(moeda, 0)
                                bandeira = get_bandeira(moeda)
                                nome = get_nome_moeda(moeda)
                                
                                # Formatar TODAS com 2 casas (exceto JPY)
                                if moeda == 'JPY':
                                    valor_fmt = f"¥ {valor:,.0f}"
                                    explicacao = "(iene não usa decimais)"
                                elif moeda == 'BRL':
                                    valor_fmt = f"R$ {valor:.2f}"
                                    explicacao = ""
                                elif moeda == 'EUR':
                                    valor_fmt = f"€ {valor:.2f}"
                                    explicacao = ""
                                elif moeda == 'GBP':
                                    valor_fmt = f"£ {valor:.2f}"
                                    explicacao = ""
                                elif moeda == 'CNY':
                                    valor_fmt = f"¥ {valor:.2f}"
                                    explicacao = ""
                                else:
                                    valor_fmt = f"{valor:.2f}"
                                    explicacao = ""
                                
                                st.markdown(f"""
                                <div class="currency-card">
                                    <div style="font-size: 2rem;">{bandeira}</div>
                                    <div class="currency-pair">USD/{moeda}</div>
                                    <div class="currency-value">{valor_fmt}</div>
                                    <div class="currency-name">{nome}</div>
                                    <div class="note">{explicacao}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Tabela comparativa
                        st.markdown("---")
                        st.subheader("📊 Tabela Comparativa")
                        
                        dados_tabela = []
                        
                        # USD
                        dados_tabela.append({
                            "Bandeira": "🇺🇸",
                            "Moeda": "USD",
                            "Nome": "Dólar Americano",
                            "Par": "USD/USD",
                            "Valor": "1,00",
                            "Unidade": "$"
                        })
                        
                        # Outras moedas
                        for moeda in moedas_cotadas:
                            valor = rates.get(moeda, 0)
                            bandeira = get_bandeira(moeda)
                            nome = get_nome_moeda(moeda)
                            
                            if moeda == 'JPY':
                                valor_fmt = f"{valor:,.0f}"
                                unidade = "¥"
                            else:
                                valor_fmt = f"{valor:.2f}"
                                if moeda == 'BRL':
                                    unidade = "R$"
                                elif moeda == 'EUR':
                                    unidade = "€"
                                elif moeda == 'GBP':
                                    unidade = "£"
                                elif moeda == 'CNY':
                                    unidade = "¥"
                                else:
                                    unidade = ""
                            
                            dados_tabela.append({
                                "Bandeira": bandeira,
                                "Moeda": moeda,
                                "Nome": nome,
                                "Par": f"USD/{moeda}",
                                "Valor": valor_fmt,
                                "Unidade": unidade
                            })
                        
                        df = pd.DataFrame(dados_tabela)
                        st.dataframe(
                            df[["Bandeira", "Moeda", "Nome", "Par", "Valor", "Unidade"]],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Gráfico com valores formatados
                        st.markdown("---")
                        st.subheader("📈 Visualização Gráfica")
                        
                        df_plot = pd.DataFrame([
                            {"Moeda": f"USD/{m}", "Taxa": rates.get(m, 0)} 
                            for m in moedas_cotadas
                        ])
                        
                        fig = px.bar(
                            df_plot,
                            x="Moeda",
                            y="Taxa",
                            title="Taxas de Câmbio (Base USD)",
                            color="Moeda",
                            text=df_plot["Taxa"].apply(lambda x: f"{x:.2f}"),
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        
                        fig.add_hline(
                            y=1.0, 
                            line_dash="dash", 
                            line_color="#f72585",
                            annotation_text="USD (base)",
                            annotation_position="bottom right"
                        )
                        
                        fig.update_layout(
                            showlegend=False,
                            height=400,
                            xaxis_title="",
                            yaxis_title="Valor em Moeda Local por 1 USD"
                        )
                        
                        fig.update_traces(
                            textposition='outside',
                            textfont_size=12
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Bitcoin
                        if dados.get('bitcoin'):
                            st.markdown("---")
                            st.subheader("₿ Bitcoin")
                            btc = dados['bitcoin']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Preço (USD)", f"${btc.get('price', 0):,.2f}")
                            with col2:
                                st.metric("Variação 24h", f"{btc.get('change_24h', 0):+.2f}%")
                            with col3:
                                st.metric("Fonte", btc.get('source', 'N/A'))
                        
                        # Recomendações
                        st.markdown("---")
                        st.subheader("💡 Recomendações")
                        
                        rec_response = requests.get(
                            f"{API_URL}/api/investment/recomendacoes",
                            timeout=10
                        )
                        
                        if rec_response.status_code == 200:
                            rec_data = rec_response.json()
                            if rec_data.get('sucesso'):
                                recomendacoes = rec_data.get('recomendacoes', [])
                                
                                for rec in recomendacoes:
                                    with st.expander(f"📌 {rec['nome']}"):
                                        st.markdown(f"""
                                        **Prazo:** {rec['prazo']}  
                                        **Risco:** {rec['risco']}  
                                        **Razão:** {rec['razao']}
                                        """)
                            else:
                                st.info("Recomendações baseadas nos dados de mercado atuais")
                    else:
                        st.error("Erro ao carregar dados da API")
                else:
                    st.error(f"Erro {response.status_code} ao conectar à API")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar ao backend. Execute: ./scripts/run_nix.sh backend")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    else:
        st.info("👆 Selecione pelo menos uma moeda para visualizar as cotações (além do USD)")
    
    # Timestamp
    st.markdown("---")
    st.caption(f"🕐 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Fonte dos dados
    st.caption("📊 Fonte: Fixer.io (dados de câmbio) • CoinGecko (Bitcoin)")