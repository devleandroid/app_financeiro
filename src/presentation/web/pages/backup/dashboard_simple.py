"""Dashboard simplificado sem plotly"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000"

def render():
    st.set_page_config(page_title="InvestSmart", page_icon="💰", layout="wide")
    
    st.title("💰 InvestSmart - Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("USD/BRL", "R$ 5,25", "-0.5%")
    with col2:
        st.metric("USD/EUR", "€ 0,92", "+0.2%")
    with col3:
        st.metric("Bitcoin", "$ 65.432", "+2.5%")
    
    st.markdown("---")
    st.info("🚧 Dashboard em construção - Plotly não está disponível")
    
    # Tabela simples
    dados = {
        'Moeda': ['BRL', 'EUR', 'GBP', 'JPY'],
        'Taxa (USD)': [5.25, 0.92, 0.79, 151.50],
        'Variação': ['-0.5%', '+0.2%', '-0.1%', '+0.8%']
    }
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True)