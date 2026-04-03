"""Páginas do Streamlit"""
import streamlit as st

# Importar as páginas
from . import login
from . import dashboard
from . import admin

def render():
    """Renderiza a página atual baseada no estado da sessão"""
    
    if st.session_state.get('admin_logado', False):
        admin.render()
    elif st.session_state.get('authenticated', False):
        dashboard.render()
    else:
        login.render()