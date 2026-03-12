# Páginas do Streamlit"""
import streamlit as st

# Importar apenas as páginas necessárias
from . import login
from . import dashboard
from . import admin

# Mapeamento de páginas
PAGINAS = {
    "login": login,
    "dashboard": dashboard,
    "admin": admin
}

def render():
    """Renderiza a página atual baseada no estado da sessão"""
    
    # Lógica de roteamento simples
    if st.session_state.get('admin_logado', False):
        pagina = "admin"
    elif st.session_state.get('authenticated', False):
        pagina = "dashboard"
    else:
        pagina = "login"
    
    # Renderizar a página
    if pagina in PAGINAS:
        PAGINAS[pagina].render()
    else:
        st.error(f"Página não encontrada: {pagina}")