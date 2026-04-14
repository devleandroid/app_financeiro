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

def verificar_senha_admin(senha: str) -> bool:
    """Verifica se a senha do admin está correta"""
    return senha == ADMIN_PASS

def render():
    st.title("💰 InvestSmart")
    st.markdown("---")
    
    # Inicializar estado da sessão
    if 'chave_atual' not in st.session_state:
        st.session_state.chave_atual = None
    if 'chave_expiracao' not in st.session_state:
        st.session_state.chave_expiracao = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if st.session_state.get('authenticated'):
        return
    
    st.caption(f"🔗 API: {API_URL}")
    
    # QUATRO ABAS
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Solicitar Acesso", 
        "🔓 Já tenho chave", 
        "⚡ Administrador",
        "📖 Como Funciona"
    ])
    
    # ============================================
    # ABA 1: Solicitar Acesso (simplificada)
    # ============================================
    with tab1:
        st.markdown("### ✉️ Solicitar chave de acesso")
        st.markdown("Digite seu email para receber uma chave de **8 dígitos** válida por **4 horas**.")
        
        email_input = st.text_input(
            "📧 Seu email", 
            placeholder="seu@email.com", 
            key="solicitar_email"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔑 Enviar chave por email", use_container_width=True, type="primary"):
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
                                    st.info("📬 **Verifique seu email!** Não esqueça a pasta de spam.")
                                else:
                                    st.error("❌ " + dados.get("mensagem", "Erro ao enviar"))
                            else:
                                st.error(f"❌ Erro {response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Erro de conexão: {e}")
                else:
                    st.warning("⚠️ Digite um email válido (ex: nome@dominio.com)")
        
        st.caption("💡 Após receber a chave, vá para a aba **'Já tenho chave'** para acessar o sistema.")
    
    # ============================================
    # ABA 2: Usar chave já recebida
    # ============================================
    with tab2:
        st.markdown("### 🔐 Entrar com Chave de Acesso")
        st.markdown("Digite a chave de **8 dígitos** que você recebeu por email.")
        
        chave_input = st.text_input(
            "Chave de acesso", 
            placeholder="Ex: ABCD1234", 
            max_chars=8, 
            key="chave_acesso"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Entrar no Sistema", use_container_width=True, type="primary"):
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
                            st.error(f"❌ Erro de conexão: {e}")
                else:
                    st.warning("⚠️ Digite uma chave válida de 8 caracteres")
        
        st.caption("💡 A chave é válida por **4 horas** e pode ser reutilizada várias vezes.")
    
    # ============================================
    # ABA 3: Administrador
    # ============================================
    with tab3:
        st.markdown("### 🔒 Área Administrativa")
        st.markdown("Acesso restrito - apenas administradores do sistema.")
        
        senha_admin = st.text_input(
            "Senha de Administrador", 
            type="password", 
            placeholder="Digite a senha", 
            key="admin_password"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔓 Entrar no Painel Admin", use_container_width=True, type="primary"):
                if senha_admin:
                    if verificar_senha_admin(senha_admin):
                        st.session_state.admin_logado = True
                        st.session_state.admin_user = "admin"
                        st.success("✅ Login realizado! Redirecionando...")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta!")
                else:
                    st.warning("⚠️ Digite a senha")
        
        st.markdown("---")
        st.caption("🔒 Área restrita - apenas para administradores autorizados.")
    
    # ============================================
    # ABA 4: Como Funciona (Guia Completo)
    # ============================================
    with tab4:
        st.markdown("## 📖 Guia do InvestSmart")
        st.markdown("Tudo o que você precisa saber para usar a plataforma.")
        
        # Seção 1: O que é
        with st.expander("🎯 O que é o InvestSmart?", expanded=True):
            st.markdown("""
            O **InvestSmart** é uma plataforma de análise de investimentos que fornece:
            
            - 💱 **Cotações em tempo real** de moedas internacionais
            - ₿ **Preço e tendência do Bitcoin**
            - 📈 **Recomendações de investimento** baseadas em dados de mercado
            - 🔐 **Acesso seguro** via chave temporária por email
            """)
        
        # Seção 2: Passo a passo
        with st.expander("📋 Passo a Passo - Como acessar", expanded=True):
            st.markdown("""
            ### 🔐 Obter sua chave de acesso
            
            | Passo | Ação |
            |-------|------|
            | **1** | Digite seu **email** na aba *"Solicitar Acesso"* |
            | **2** | Clique em **"Enviar chave por email"** |
            | **3** | Verifique sua caixa de entrada (e o **spam**) |
            | **4** | Copie a **chave de 8 dígitos** recebida |
            | **5** | Vá para a aba *"Já tenho chave"* |
            | **6** | Cole a chave e clique em **"Entrar"** |
            
            > ⏰ **Atenção:** A chave é válida por **4 horas** e pode ser reutilizada várias vezes neste período.
            """)
        
        # Seção 3: Funcionalidades
        with st.expander("📊 Funcionalidades do Dashboard", expanded=True):
            st.markdown("""
            Após o login, você terá acesso a:
            
            ### 💱 Câmbio em Tempo Real
            - Cotações de moedas como **USD, BRL, EUR, GBP, JPY, CNY**
            - Gráficos interativos e tabelas comparativas
            - Variação percentual das moedas
            
            ### ₿ Bitcoin
            - Preço atual do Bitcoin em Dólar (USD)
            - Variação nas últimas 24 horas
            - Fonte: **CoinGecko**
            
            ### 💡 Recomendações
            - Sugestões de investimento baseadas em:
              - Força/fracura do Real (BRL)
              - Cotação do Euro (EUR)
              - Preço do Bitcoin (BTC)
              - Cenário econômico geral
            """)
        
        # Seção 4: Dúvidas frequentes
        with st.expander("❓ Dúvidas Frequentes", expanded=True):
            st.markdown("""
            **❌ Não recebi o email com a chave?**
            > Verifique sua caixa de **spam** ou **lixo eletrônico**. Se ainda assim não encontrar, tente novamente com outro email ou aguarde alguns minutos.
            
            **⏰ Minha chave expirou?**
            > As chaves têm validade de **4 horas**. Se expirou, solicite uma nova na aba *"Solicitar Acesso"*.
            
            **🔄 Posso reutilizar a mesma chave?**
            > Sim! A mesma chave funciona para múltiplos acessos dentro do período de 4 horas.
            
            **🔒 Esqueci minha chave?**
            > Solicite uma nova chave. A chave anterior será substituída automaticamente.
            
            **📊 Os dados são reais?**
            > Sim! As cotações vêm da API **Fixer.io** (taxas de câmbio) e **CoinGecko** (Bitcoin). Em caso de indisponibilidade, usamos dados simulados.
            
            **🛡️ O sistema é seguro?**
            > Sim! As chaves são geradas aleatoriamente, enviadas por email e expiram após 4 horas. O painel administrativo é protegido por senha.
            """)
        
        # Seção 5: Tecnologias
        with st.expander("⚙️ Tecnologias Utilizadas", expanded=True):
            st.markdown("""
            | Componente | Tecnologia |
            |------------|------------|
            | **Backend** | FastAPI + Uvicorn |
            | **Frontend** | Streamlit + Plotly |
            | **Banco de Dados** | SQLite (local) / PostgreSQL (produção) |
            | **APIs Externas** | Fixer.io (câmbio), CoinGecko (Bitcoin) |
            | **Infraestrutura** | Docker, Koyeb, Streamlit Cloud |
            """)
        
        # Seção 6: Suporte
        with st.expander("📞 Suporte e Contato", expanded=True):
            st.markdown("""
            ### Precisa de ajuda?
            
            - 📧 **Email de suporte:** suporte@investsmart.com
            - 📖 **Documentação completa:** [docs.investsmart.com](https://docs.investsmart.com)
            - 💬 **Reportar problema:** Abra uma issue no [GitHub](https://github.com/devleandroid/app_financeiro/issues)
            
            ---
            
            *O InvestSmart é um projeto educacional. As recomendações não constituem aconselhamento financeiro profissional.*
            """)
        
        # Rodapé da aba
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 0.8rem;'>"
            "© 2026 InvestSmart - Análise de Investimentos em Tempo Real"
            "</p>", 
            unsafe_allow_html=True
        )
    
    # Rodapé geral (aparece em todas as abas)
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #999; font-size: 0.7rem;'>"
        "📊 Dados fornecidos por Fixer.io • ₿ Bitcoin via CoinGecko"
        "</p>", 
        unsafe_allow_html=True
    )
