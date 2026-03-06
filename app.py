# app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .login-container {
        max-width: 500px;
        margin: 50px auto;
        padding: 30px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .login-header h1 {
        color: #4361ee;
        font-size: 2.5rem;
        margin: 10px 0;
    }
    
    .chave-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-family: monospace;
        font-size: 32px;
        text-align: center;
        letter-spacing: 8px;
        margin: 20px 0;
        font-weight: bold;
    }
    
    .timer-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        border-left: 5px solid #f72585;
    }
    
    .timer-text {
        color: #f72585;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .info-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #4361ee;
    }
    
    .dashboard-header {
        background: linear-gradient(135deg, #4361ee, #3f37c9);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.8rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Configuração da página
st.set_page_config(
    page_title="InvestSmart - Análise de Investimentos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API
API_URL = "http://localhost:8000"

# ============================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ============================================
def init_session_state():
    if 'acesso_liberado' not in st.session_state:
        st.session_state.acesso_liberado = False
    if 'usuario_email' not in st.session_state:
        st.session_state.usuario_email = None
    if 'dados' not in st.session_state:
        st.session_state.dados = None
    if 'ultima_atualizacao' not in st.session_state:
        st.session_state.ultima_atualizacao = None
    if 'moedas_selecionadas' not in st.session_state:
        st.session_state.moedas_selecionadas = ['BRL', 'USD', 'EUR', 'GBP', 'CNY']

# ============================================
# TELA DE LOGIN COM CHAVE
# ============================================
def render_login():
    """Tela de login com solicitação de chave"""
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/000000/investment.png", width=80)
    st.markdown("<h1>💰 InvestSmart</h1>", unsafe_allow_html=True)
    st.markdown("<p>Acesso Seguro por Chave Temporária</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Abas
    tab1, tab2 = st.tabs(["🔑 Solicitar Acesso", "🔓 Já tenho chave"])
    
    with tab1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **📋 Como funciona:**
        1. Digite seu email abaixo
        2. Receberá uma chave de 8 dígitos
        3. A chave é válida por **4 horas**
        4 Use a chave na aba ao lado
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("solicitar_form"):
            email = st.text_input(
                "Seu melhor email",
                placeholder="exemplo@email.com",
                help="Enviaremos a chave de acesso para este email"
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button(
                    "📧 Enviar chave por email",
                    use_container_width=True,
                    type="primary"
                )
            
            if submit:
                if email and '@' in email and '.' in email:
                    with st.spinner("Enviando chave..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/solicitar-chave",
                                json={"email": email}
                            )
                            dados = response.json()
                            
                            if dados.get("sucesso"):
                                st.success("✅ " + dados["mensagem"])
                                st.balloons()
                                
                                # Se a chave veio na resposta (modo debug)
                                if "chave:" in dados["mensagem"].lower():
                                    chave = dados["mensagem"].split(":")[-1].strip()
                                    st.code(chave, language="text")
                            else:
                                st.error("❌ " + dados["mensagem"])
                        except Exception as e:
                            st.error(f"❌ Erro de conexão: {e}")
                else:
                    st.warning("⚠️ Digite um email válido")
    
    with tab2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **🔑 Já tem sua chave?**
        Digite abaixo os 8 caracteres recebidos por email.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("validar_form"):
            chave = st.text_input(
                "Chave de acesso",
                placeholder="EX: ABCD1234",
                max_chars=8,
                help="Digite os 8 caracteres da chave (maiúsculas e números)"
            ).upper()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                validar = st.form_submit_button(
                    "🔓 Acessar Dashboard",
                    use_container_width=True,
                    type="primary"
                )
            
            if validar:
                if chave and len(chave) == 8:
                    with st.spinner("Validando chave..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/validar-chave",
                                json={"chave": chave}
                            )
                            dados = response.json()
                            
                            if dados.get("sucesso"):
                                st.success("✅ " + dados["mensagem"])
                                st.session_state.acesso_liberado = True
                                st.session_state.usuario_email = dados.get("email")
                                st.rerun()
                            else:
                                st.error("❌ " + dados["mensagem"])
                        except Exception as e:
                            st.error(f"❌ Erro de conexão: {e}")
                else:
                    st.warning("⚠️ Digite uma chave válida de 8 caracteres")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# FUNÇÕES DO DASHBOARD
# ============================================
def buscar_dados_api(moedas):
    """Busca dados da API com timeout maior"""
    try:
        moedas_str = ",".join(moedas)
        response = requests.get(
            f"{API_URL}/api/dados-completos",
            params={"moedas": moedas_str},
            timeout=30  # <--- AUMENTE DE 10 PARA 30 SEGUNDOS
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏰ O servidor demorou muito para responder. Tente novamente.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar ao backend. Certifique-se de que o FastAPI está rodando.")
        return None
    except Exception as e:
        st.error(f"❌ Erro na requisição: {e}")
        return None

def render_sidebar():
    """Renderiza barra lateral"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/investment.png", width=80)
        st.markdown(f"**👤 {st.session_state.usuario_email}**")
        st.markdown("---")
        
        # Botão de atualizar
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.session_state.dados = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🌍 Moedas")
        
        todas_moedas = ['USD', 'BRL', 'EUR', 'GBP', 'CNY', 'JPY', 'RUB']
        selecionadas = []
        
        for moeda in todas_moedas:
            if st.checkbox(moeda, value=moeda in st.session_state.moedas_selecionadas):
                selecionadas.append(moeda)
        
        if selecionadas:
            st.session_state.moedas_selecionadas = selecionadas
        
        if st.button("📊 Aplicar Filtros", use_container_width=True):
            st.session_state.dados = None
            st.rerun()

def render_dashboard():
    """Renderiza o dashboard principal"""
    
    render_sidebar()
    
    # Cabeçalho
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>📊 Dashboard de Mercado</h1>
        <p>Bem-vindo, {st.session_state.usuario_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buscar dados
    if st.session_state.dados is None:
        with st.spinner("🔄 Carregando dados..."):
            dados = buscar_dados_api(st.session_state.moedas_selecionadas)
            if dados:
                st.session_state.dados = dados
                st.session_state.ultima_atualizacao = datetime.now()
    
    # Exibir dados
    if st.session_state.dados:
        dados = st.session_state.dados
        
        if dados.get("sucesso"):
            # Cards de resumo
            cambio = dados['dados_brutos']['cambio']
            bitcoin = dados['dados_brutos']['bitcoin']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'BRL' in cambio:
                    st.metric("USD/BRL", f"R$ {cambio['BRL']:.2f}")
            
            with col2:
                if 'EUR' in cambio:
                    st.metric("USD/EUR", f"€ {cambio['EUR']:.4f}")
            
            with col3:
                if bitcoin.get('preco'):
                    st.metric("Bitcoin", f"$ {bitcoin['preco']['price']:,.2f}")
            
            with col4:
                if st.session_state.ultima_atualizacao:
                    st.metric("Atualizado", 
                             st.session_state.ultima_atualizacao.strftime("%H:%M:%S"))
            
            st.markdown("---")
            
            # Recomendações
            st.subheader("💡 Recomendações")
            recomendacoes = dados.get('recomendacoes', [])
            
            for rec in recomendacoes:
                with st.expander(f"📌 {rec['nome']}"):
                    st.markdown(f"""
                    **Prazo:** {rec['prazo']}  
                    **Risco:** {rec['risco']}  
                    **Razão:** {rec['razao']}
                    """)
        else:
            st.error("Erro ao carregar dados")

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    init_session_state()
    
    if not st.session_state.acesso_liberado:
        render_login()
    else:
        render_dashboard()
        
        # Rodapé
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <p>© 2024 InvestSmart - Projeto Educacional</p>
            <p>Dados fornecidos por Fixer.io | Chaves expiram em 4 horas</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()