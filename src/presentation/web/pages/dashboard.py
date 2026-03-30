# Dashboard principal simplificado"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def formatar_taxa(moeda: str, valor: float) -> str:
    """Formata a taxa de câmbio com 2 casas decimais para todas as moedas"""
    if moeda == 'USD':
        return f"$ 1,00"
    elif moeda == 'JPY':
        return f"¥ {valor:,.0f}"
    else:
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

def calcular_variacao(valor_anterior, valor_atual):
    """Calcula a variação percentual entre dois valores"""
    if valor_anterior and valor_anterior > 0:
        return ((valor_atual - valor_anterior) / valor_anterior) * 100
    return 0

def buscar_historico(moeda: str) -> dict:
    """Busca histórico da moeda na API"""
    try:
        response = requests.get(
            f"{API_URL}/api/investment/historico",
            params={"moeda": moeda},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def inicializar_estado():
    """Inicializa todas as variáveis de estado da sessão - ESSENCIAL para evitar KeyError"""
    if 'historico' not in st.session_state:
        st.session_state.historico = {}
    if 'historico_anterior' not in st.session_state:
        st.session_state.historico_anterior = {}
    if 'ultima_atualizacao' not in st.session_state:
        st.session_state.ultima_atualizacao = datetime.now()
    if 'moedas_selecionadas' not in st.session_state:
        st.session_state.moedas_selecionadas = ['USD', 'BRL', 'EUR', 'GBP']

@st.cache_data(ttl=0)
def buscar_dados(moedas):
    """Busca dados da API sem cache"""
    try:
        response = requests.get(
            f"{API_URL}/api/investment/dados",
            params={"moedas": ",".join(moedas)},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Erro na requisição: {e}")
    return None

def render():
    """Renderiza o dashboard"""
    
    # INICIALIZAR ESTADO PRIMEIRO (resolve o erro!)
    inicializar_estado()
    
    # Verificar autenticação
    if not st.session_state.get('authenticated'):
        st.warning("Você precisa fazer login primeiro")
        if st.button("← Voltar ao login"):
            st.session_state.authenticated = False
            st.rerun()
        return
    
    # Header com logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("📊 Dashboard de Câmbio")
    with col2:
        if st.button("🚪 Sair", use_container_width=True):
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
        .currency-variation {
            font-size: 0.9rem;
            padding: 0.2rem 0.8rem;
            border-radius: 20px;
            display: inline-block;
        }
        .positive {
            background: #d4edda;
            color: #155724;
        }
        .negative {
            background: #f8d7da;
            color: #721c24;
        }
        .neutral {
            background: #e2e3e5;
            color: #383d41;
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
        .update-button-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        /* Estilo para os links das fontes */
        .source-link {
            text-align: center;
            margin-top: 2rem;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.8rem;
        }
        .source-link a {
            color: #4361ee;
            text-decoration: none;
            margin: 0 0.5rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            transition: background 0.3s ease;
        }
        .source-link a:hover {
            background: #e9ecef;
            text-decoration: underline;
        }
        .source-link span {
            color: #666;
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
    moedas_selecionadas = ['USD']  # USD sempre incluso
    
    for i, moeda in enumerate(todas_moedas):
        with cols[i % 4]:
            bandeira = get_bandeira(moeda)
            nome = get_nome_moeda(moeda)
            if st.checkbox(f"{bandeira} {moeda} - {nome}", 
                          value=moeda in st.session_state.moedas_selecionadas, 
                          key=f"cb_{moeda}"):
                moedas_selecionadas.append(moeda)
    
    # Atualizar seleção no estado
    st.session_state.moedas_selecionadas = moedas_selecionadas
    
    st.markdown("---")
    
    # Título com botão de atualizar
    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader("💰 Cotações em Tempo Real")
    with col2:
        if st.button("🔄 Atualizar", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.session_state.ultima_atualizacao = datetime.now()
            st.rerun()
    
    st.caption(f"🕐 Última atualização: {st.session_state.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Buscar dados
    if len(moedas_selecionadas) > 1:
        with st.spinner("🔄 Carregando dados do Fixer.io..."):
            dados = buscar_dados(moedas_selecionadas)
            
            if dados and dados.get('sucesso'):
                rates = dados['dados']
                
                # Atualizar timestamp
                st.session_state.ultima_atualizacao = datetime.now()
                
                # Data da cotação
                st.caption(f"Data da cotação: {dados.get('data', datetime.now().strftime('%Y-%m-%d'))}")
                
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
                moedas_cotadas = [m for m in moedas_selecionadas if m != 'USD']
                
                if moedas_cotadas:
                    cols = st.columns(len(moedas_cotadas))
                    
                    # Salvar histórico anterior para calcular variação
                    historico_anterior = st.session_state.historico.copy()
                    
                    for i, moeda in enumerate(moedas_cotadas):
                        with cols[i]:
                            valor = rates.get(moeda, 0)
                            bandeira = get_bandeira(moeda)
                            nome = get_nome_moeda(moeda)
                            
                            # Calcular variação usando histórico anterior
                            historico = buscar_historico(moeda)
                            if historico and historico.get("sucesso"):
                                variacao = historico.get("variacao_24h", 0)
                            else:
                                variacao = 0
                            
                            # Atualizar histórico
                            st.session_state.historico[moeda] = valor
                            
                            # Determinar classe da variação
                            if variacao > 0:
                                var_class = "positive"
                                var_sinal = "▲"
                            elif variacao < 0:
                                var_class = "negative"
                                var_sinal = "▼"
                            else:
                                var_class = "neutral"
                                var_sinal = "●"
                            
                            # Formatar valor
                            if moeda == 'JPY':
                                valor_fmt = f"¥ {valor:,.0f}"
                                explicacao = "(iene não usa decimais)"
                            else:
                                if moeda == 'BRL':
                                    valor_fmt = f"R$ {valor:.2f}"
                                elif moeda == 'EUR':
                                    valor_fmt = f"€ {valor:.2f}"
                                elif moeda == 'GBP':
                                    valor_fmt = f"£ {valor:.2f}"
                                elif moeda == 'CNY':
                                    valor_fmt = f"¥ {valor:.2f}"
                                else:
                                    valor_fmt = f"{valor:.2f}"
                                explicacao = ""
                            
                            st.markdown(f"""
                            <div class="currency-card">
                                <div style="font-size: 2rem;">{bandeira}</div>
                                <div class="currency-pair">USD/{moeda}</div>
                                <div class="currency-value">{valor_fmt}</div>
                                <div class="currency-variation {var_class}">{var_sinal} {abs(variacao):.2f}%</div>
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
                        "Unidade": "$",
                        "Variação": "-"
                    })
                    
                    # Definir dicionário de unidades no início do arquivo
                    UNIDADES = {
                        'USD': '$',
                        'BRL': 'R$',
                        'EUR': '€',
                        'GBP': '£',
                        'JPY': '¥',
                        'CNY': '¥',
                        'CHF': '₣',
                        'CAD': 'C$',
                        'AUD': 'A$',
                        'CHF': '₣'  # Franco Suíço
                    }

                    # Outras moedas
                    for moeda in moedas_cotadas:
                        valor = rates.get(moeda, 0)
                        bandeira = get_bandeira(moeda)
                        nome = get_nome_moeda(moeda)
                        
                        # Calcular variação usando histórico anterior
                        variacao = 0
                        if moeda in historico_anterior:
                            variacao = calcular_variacao(historico_anterior[moeda], valor)
                        
                        var_texto = f"{variacao:+.2f}%" if variacao != 0 else "0.00%"
                        
                        # Formatar valor
                        if moeda == 'JPY':
                            valor_fmt = f"{valor:,.0f}"
                        else:
                            valor_fmt = f"{valor:.2f}"
                        
                        # Pegar unidade do dicionário
                        unidade = UNIDADES.get(moeda, "")
                        
                        dados_tabela.append({
                            "Bandeira": bandeira,
                            "Moeda": moeda,
                            "Nome": nome,
                            "Par": f"USD/{moeda}",
                            "Valor": valor_fmt,
                            "Unidade": unidade,
                            "Variação": var_texto
                        })
                    
                    df = pd.DataFrame(dados_tabela)
                    st.dataframe(
                        df[["Bandeira", "Moeda", "Nome", "Par", "Valor", "Unidade", "Variação"]],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Gráfico
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
                        text=df_plot["Taxa"].apply(lambda x: f"{x:,.0f}" if x > 100 else f"{x:.2f}"),
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    
                    fig.add_hline(
                        y=1.0, 
                        line_dash="dash", 
                        line_color="#f72585",
                        annotation_text="USD (base)",
                        annotation_position="bottom right"
                    )

                    # AJUSTES PARA GARANTIR QUE NÃO CORTE
                    fig.update_layout(
                        showlegend=False,
                        height=450,  # Aumentar altura
                        xaxis_title="",
                        yaxis_title="Valor em Moeda Local por 1 USD",
                        # Margens para evitar corte
                        margin=dict(t=50, l=50, r=50, b=80),
                        # Ajuste para texto das barras não cortar
                        uniformtext_minsize=10,
                        uniformtext_mode='hide'
                    )

                    # Ajustar posição do texto
                    fig.update_traces(
                        textposition='outside',
                        textfont_size=12,
                        # Garantir que texto não seja cortado
                        cliponaxis=False
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
                            st.metric("Fonte", "CoinGecko")
                    
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
                    st.info("Selecione outras moedas além do USD para visualizar as cotações")
            else:
                st.error("Erro ao carregar dados da API")
    else:
        st.info("👆 Selecione pelo menos uma moeda para visualizar as cotações (além do USD)")
    
    # Fontes dos dados - VERSÃO CORRIGIDA com links abreviados
    st.markdown("""
    <div class="source-link">
        <span>📊 Fontes:</span>
        <a href="https://fixer.io" target="_blank">Fixer.io</a>
        <span>•</span>
        <a href="https://www.coingecko.com" target="_blank">CoinGecko</a>
    </div>
    """, unsafe_allow_html=True)