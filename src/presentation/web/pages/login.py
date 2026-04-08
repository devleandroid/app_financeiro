"""Página de login """
import streamlit as st
import requests
import os
from datetime import datetime

# Carregar variáveis do arquivo .env manualmente
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

# ============================================
# FUNÇÃO DE VERIFICAÇÃO (DEFINIDA ANTES DE USAR)
# ============================================
def verificar_senha_admin(senha: str) -> bool:
    """Verifica se a senha do admin está correta"""
    return senha == ADMIN_PASS

# ============================================
# FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO
# ============================================
def render():
    """Renderiza a página de login"""
    st.title("💰 InvestSmart")
    st.markdown("---")
    
    # Inicializar estado da sessão
    if 'chave_atual' not in st.session_state:
        st.session_state.chave_atual = None
    if 'chave_expiracao' not in st.session_state:
        st.session_state.chave_expiracao = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    # Verificar se já está logado como usuário
    if st.session_state.get('authenticated'):
        return
    
    # Informações de debug
    st.caption(f"🔗 API: {API_URL}")
    st.caption(f"🔧 ADMIN_PASS configurada: {'✅ Sim' if ADMIN_PASS != 'admin123' else '⚠️ Usando padrão'}")
    
    # Três abas
    tab1, tab2, tab3 = st.tabs(["👤 Solicitar Acesso", "🔓 Já tenho chave", "⚡ Administrador"])
    
    # ABA 1: Solicitar chave
    with tab1:
        st.markdown("### 📧 Solicitar Chave de Acesso")
        st.markdown("Digite seu email para receber uma chave de acesso válida por 4 horas.")
        
        email_input = st.text_input("Email", placeholder="seu@email.com", key="solicitar_email")
        
        if st.button("🔑 Enviar chave por email", use_container_width=True):
            if email_input and '@' in email_input:
                with st.spinner("Enviando..."):
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
                                st.info("📧 Verifique sua caixa de entrada e a pasta de spam.")
                            else:
                                st.error(dados.get("mensagem", "Erro"))
                        else:
                            st.error(f"Erro {response.status_code}")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")
            else:
                st.warning("Digite um email válido")
    
    # ABA 2: Usar chave já recebida
    with tab2:
        st.markdown("### 🔐 Entrar com Chave de Acesso")
        st.markdown("Digite a chave de 8 dígitos que você recebeu por email.")
        
        chave_input = st.text_input("Chave de acesso", placeholder="ABCD1234", max_chars=8, key="chave_acesso")
        
        if st.button("🚪 Entrar no Sistema", use_container_width=True, type="primary"):
            if chave_input and len(chave_input) == 8:
                with st.spinner("Validando..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/validar-chave",
                            json={"chave": chave_input.upper()},
                            timeout=10
                        )
                        if response.status_code == 200:
                            dados = response.json()
                            if dados.get("sucesso"):
                                email_usuario = dados.get("email")
                                st.session_state.authenticated = True
                                st.session_state.user_email = dados.get("email")
                                st.session_state.chave_atual = chave_input.upper()
                                st.session_state.chave_expiracao = dados.get("expira_em")
                                st.success(dados.get("mensagem"))
                                st.rerun()
                            else:
                                st.error(dados.get("mensagem", "Chave inválida"))
                        else:
                            st.error(f"Erro {response.status_code}")
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.warning("Digite uma chave de 8 caracteres")

    # ABA 3: ADMIN (login direto)
    with tab3:
        st.markdown("### 🔒 Área Administrativa")
        st.markdown("Acesso restrito - apenas administradores")
        
        # Campo de senha (sem debug)
        senha_admin = st.text_input(
            "Senha de Administrador", 
            type="password", 
            placeholder="Digite a senha", 
            key="admin_password"
        )
        
        # Botão de login do admin
        if st.button("🔓 Entrar no Painel Admin", use_container_width=True, type="primary"):
            if senha_admin:
                if verificar_senha_admin(senha_admin):
                    st.session_state.admin_logado = True
                    st.session_state.admin_user = "admin"
                    st.success("✅ Login realizado! Redirecionando...")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
                    st.caption(f"🔧 Debug: Digitado = '{senha_admin}', Esperado = '{ADMIN_PASS}'")
            else:
                st.warning("Digite a senha")
        
        st.markdown("---")
        st.caption("🔒 Acesso restrito - apenas administradores")
