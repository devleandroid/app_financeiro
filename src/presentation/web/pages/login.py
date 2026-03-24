"""Página de login simplificada"""
import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.caption(f"🔗 Conectando a: {API_URL}")
# Tetnta ler do secrets.toml, depois do ambiente
try:
    API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))
except:
    API_URL = os.getenv("API_URL", "http://localhost:8000")
def render():
    """Renderiza a página de login"""
    
    # CSS minimalista
    st.markdown("""
    <style>
        .main-title {
            text-align: center;
            color: #4361ee;
            font-size: 3rem;
            margin-bottom: 0;
        }
        .sub-title {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .login-box {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .admin-link {
            text-align: center;
            margin-top: 2rem;
            color: #999;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Título
    st.markdown('<h1 class="main-title">💰 InvestSmart</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Análise de Investimentos</p>', unsafe_allow_html=True)
    
    # Abas: Usuário e Admin
    tab1, tab2 = st.tabs(["👤 Usuário", "⚡ Administrador"])
    
    with tab1:
        with st.container():
            # st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
            # Email
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            
            # Botão de solicitar chave
            if st.button("🔑 Solicitar chave de acesso", use_container_width=True):
                if email and '@' in email:
                    with st.spinner("Enviando..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/solicitar-chave",
                                json={"email": email},
                                timeout=10
                            )
                            if response.status_code == 200:
                                dados = response.json()
                                if dados.get("sucesso"):
                                    st.success("✅ Chave enviada! Verifique seu email.")
                                    st.info("📧 A chave será mostrada no terminal do backend (modo desenvolvimento)")
                                else:
                                    st.error(dados.get('mensagem', 'Erro'))
                            else:
                                st.error(f"Erro {response.status_code}")
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")
                else:
                    st.warning("Digite um email válido")
            
            st.markdown("---")
            
            # Chave
            chave = st.text_input("🔐 Chave de acesso", placeholder="ABCD1234", max_chars=8)
            
            if st.button("🚪 Entrar no sistema", use_container_width=True, type="primary"):
                if chave and len(chave) == 8:
                    with st.spinner("Validando..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/validar-chave",
                                json={"chave": chave.upper()},
                                timeout=10
                            )
                            if response.status_code == 200:
                                dados = response.json()
                                if dados.get("sucesso"):
                                    st.session_state.authenticated = True
                                    st.session_state.user_email = dados.get("email", email)
                                    st.rerun()
                                else:
                                    st.error(dados.get('mensagem', 'Chave inválida'))
                            else:
                                st.error(f"Erro {response.status_code}")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                else:
                    st.warning("Digite uma chave de 8 caracteres")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            # st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.markdown("### 🔒 Área Restrita")
            
            username = st.text_input("👤 Usuário", placeholder="admin")
            password = st.text_input("🔐 Senha", type="password", placeholder="••••••••")
            
            if st.button("🔓 Entrar como Admin", use_container_width=True, type="primary"):
                # Por enquanto, credenciais fixas (depois integrar com API)
                if username == "admin" and password == "admin123":
                    st.session_state.admin_logado = True
                    st.session_state.admin_user = username
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #999; font-size: 0.8rem;">© 2026 InvestSmart</p>', unsafe_allow_html=True)