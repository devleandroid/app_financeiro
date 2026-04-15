"""Página de login responsiva com segurança"""
import streamlit as st
import requests
import os
import time
from datetime import datetime

# Carregar variáveis do arquivo .env
env_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

API_URL = os.getenv("API_URL", "http://localhost:8000")
ADMIN_PASS = os.getenv("ADMIN_PASS") or os.getenv("ADMIN_PASSWORD") or "admin123"

# Controle de tentativas (em memória)
if 'admin_attempts' not in st.session_state:
    st.session_state.admin_attempts = 0
if 'admin_blocked_until' not in st.session_state:
    st.session_state.admin_blocked_until = None

def verificar_senha_admin(senha: str) -> bool:
    return senha == ADMIN_PASS

def render():
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            position: relative;
        }
        @media (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"]::after {
                content: "← →";
                position: absolute;
                right: 5px;
                bottom: -20px;
                font-size: 0.7rem;
                color: #999;
                opacity: 0.7;
            }
        }
        .tab-indicator {
            text-align: center;
            font-size: 0.7rem;
            color: #999;
            margin-top: -10px;
            margin-bottom: 10px;
            display: block;
        }
        @media (min-width: 769px) {
            .tab-indicator { display: none; }
        }
        .security-notice {
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 8px;
            font-size: 0.7rem;
            color: #666;
            text-align: center;
            margin-top: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💰 InvestSmart")
    st.markdown('<div class="tab-indicator">👆 Toque nas abas para navegar</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if 'chave_atual' not in st.session_state:
        st.session_state.chave_atual = None
    if 'chave_expiracao' not in st.session_state:
        st.session_state.chave_expiracao = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if st.session_state.get('authenticated'):
        return
    
    st.caption(f"🔗 API: {API_URL}")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📧 Solicitar", "🔑 Acessar", "⚙️ Admin", "❓ Ajuda"
    ])
    
    # ============================================
    # ABA 1: Solicitar Acesso
    # ============================================
    with tab1:
        st.markdown("### ✉️ Solicitar chave")
        email_input = st.text_input("📧 Seu email", placeholder="seu@email.com", key="solicitar_email")
        
        if st.button("📨 Enviar chave", use_container_width=True, type="primary"):
            if email_input and '@' in email_input and '.' in email_input:
                with st.spinner("📧 Enviando..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/solicitar-chave",
                            json={"email": email_input},
                            timeout=10
                        )
                        if response.status_code == 200:
                            dados = response.json()
                            if dados.get("sucesso"):
                                st.success("✅ " + dados.get("mensagem", ""))
                                st.balloons()
                                st.info("📬 Verifique seu email (incluindo spam)")
                            else:
                                st.error("❌ " + dados.get("mensagem", "Erro"))
                        else:
                            st.error(f"❌ Erro {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro de conexão: {e}")
            else:
                st.warning("⚠️ Digite um email válido")
        st.caption("💡 A chave chega em minutos e vale por 4 horas")
    
    # ============================================
    # ABA 2: Acessar com chave
    # ============================================
    with tab2:
        st.markdown("### 🔐 Entrar no sistema")
        chave_input = st.text_input("Chave de 8 dígitos", placeholder="Ex: ABCD1234", max_chars=8, key="chave_acesso")
        
        if st.button("🚪 Entrar", use_container_width=True, type="primary"):
            if chave_input and len(chave_input) == 8:
                with st.spinner("🔍 Validando..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/validar-chave",
                            json={"chave": chave_input.upper()},
                            timeout=10
                        )
                        if response.status_code == 200:
                            dados = response.json()
                            if dados.get("sucesso"):
                                st.session_state.authenticated = True
                                st.session_state.user_email = dados.get("email")
                                st.session_state.chave_atual = chave_input.upper()
                                st.session_state.chave_expiracao = dados.get("expira_em")
                                st.success("✅ " + dados.get("mensagem"))
                                st.rerun()
                            else:
                                st.error("❌ " + dados.get("mensagem", "Chave inválida"))
                        else:
                            st.error(f"❌ Erro {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
            else:
                st.warning("⚠️ Digite uma chave de 8 caracteres")
        st.caption("💡 A chave funciona por 4 horas e pode ser reutilizada")
    
    # ============================================
    # ABA 3: Administrador (COM PROTEÇÃO)
    # ============================================
    with tab3:
        st.markdown("### 🔒 Área Administrativa")
        st.markdown("Acesso restrito - apenas administradores autorizados.")
        
        # Verificar se está bloqueado
        if st.session_state.admin_blocked_until:
            if time.time() < st.session_state.admin_blocked_until:
                remaining = int(st.session_state.admin_blocked_until - time.time())
                st.error(f"🔒 Muitas tentativas incorretas. Aguarde {remaining} segundos.")
                st.warning("⚠️ Tentativas repetidas serão registradas para segurança.")
                return
            else:
                # Resetar bloqueio
                st.session_state.admin_blocked_until = None
                st.session_state.admin_attempts = 0
        
        senha_admin = st.text_input("Senha de Administrador", type="password", placeholder="Digite a senha", key="admin_password")
        
        # Mostrar tentativas restantes
        if st.session_state.admin_attempts > 0:
            remaining = 5 - st.session_state.admin_attempts
            st.warning(f"⚠️ Tentativas restantes: {remaining}")
        
        if st.button("🔓 Entrar no Painel Admin", use_container_width=True, type="primary"):
            if senha_admin:
                if verificar_senha_admin(senha_admin):
                    # Login bem-sucedido - resetar contador
                    st.session_state.admin_attempts = 0
                    st.session_state.admin_logado = True
                    st.session_state.admin_user = "admin"
                    st.success("✅ Login realizado! Redirecionando...")
                    st.rerun()
                else:
                    # Login falhou - incrementar contador
                    st.session_state.admin_attempts += 1
                    
                    # Bloquear após 5 tentativas
                    if st.session_state.admin_attempts >= 5:
                        st.session_state.admin_blocked_until = time.time() + 300  # 5 minutos
                        st.error("🔒 Número máximo de tentativas excedido. Aguarde 5 minutos.")
                        st.warning("⚠️ Esta tentativa foi registrada para fins de segurança.")
                    else:
                        st.error(f"❌ Senha incorreta! Tentativa {st.session_state.admin_attempts} de 5.")
            else:
                st.warning("⚠️ Digite a senha")
        
        # Aviso de segurança
        st.markdown("""
        <div class="security-notice">
        🔒 <strong>Segurança</strong><br>
        • Todas as tentativas de acesso são registradas<br>
        • Após 5 tentativas falhas, acesso bloqueado por 5 minutos<br>
        • Nunca compartilhe suas credenciais
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # ABA 4: Ajuda
    # ============================================
    with tab4:
        st.markdown("### ❓ Como usar o InvestSmart")
        
        with st.expander("📖 Passo a passo", expanded=True):
            st.markdown("""
            **1️⃣ Solicitar chave**
            - Digite seu email na aba **"Solicitar"**
            - Clique em **"Enviar chave"**
            - Aguarde o email (verifique o spam)
            
            **2️⃣ Acessar o sistema**
            - Vá para a aba **"Acessar"**
            - Digite a chave de 8 dígitos
            - Clique em **"Entrar"**
            
            **3️⃣ Explorar o dashboard**
            - Visualize cotações de moedas
            - Acompanhe o preço do Bitcoin
            - Veja recomendações de investimento
            """)
        
        with st.expander("❓ Dúvidas frequentes", expanded=False):
            st.markdown("""
            **⏰ Quanto tempo a chave é válida?**
            > 4 horas a partir do envio.
            
            **🔄 Posso reutilizar a mesma chave?**
            > Sim! Durante as 4 horas de validade.
            
            **📧 Não recebi o email?**
            > Verifique sua caixa de spam.
            
            **📊 Os dados são reais?**
            > Sim, vêm da API Fixer.io e CoinGecko.
            """)
        
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; font-size: 0.8rem;'>"
            "📧 Suporte: suporte@investsmart.com"
            "</p>", 
            unsafe_allow_html=True
        )
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #999; font-size: 0.7rem;'>"
        "📊 Dados: Fixer.io • ₿ Bitcoin: CoinGecko"
        "</p>", 
        unsafe_allow_html=True
    )
