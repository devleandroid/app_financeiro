# scripts/relatorio_email.py
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))
from database import db

load_dotenv()

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", EMAIL_REMETENTE)

def gerar_html_relatorio():
    """Gera relatório em HTML"""
    
    relatorio = db.gerar_relatorio_semanal()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background: #4361ee; color: white; padding: 20px; text-align: center; }}
            .stats {{ display: flex; gap: 20px; margin: 20px; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; flex: 1; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #4361ee; color: white; padding: 10px; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Relatório Semanal - InvestSmart</h1>
            <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h2>{relatorio['total_solicitacoes']}</h2>
                <p>Solicitações</p>
            </div>
            <div class="stat-card">
                <h2>{relatorio['total_acessos']}</h2>
                <p>Acessos</p>
            </div>
            <div class="stat-card">
                <h2>{relatorio['total_emails_solicitaram']}</h2>
                <p>Emails Únicos</p>
            </div>
        </div>
    """
    
    # Lista de emails
    if relatorio['emails_solicitacoes']:
        html += "<h2>📧 Emails que Solicitaram</h2>"
        html += "<table><tr><th>Email</th><th>Data</th></tr>"
        for email in relatorio['emails_solicitacoes']:
            html += f"<tr><td>{email['email']}</td><td>{email['primeira_solicitacao']}</td></tr>"
        html += "</table>"
    
    html += """
        <p style="text-align: center; color: gray; margin-top: 30px;">
            Relatório automático do InvestSmart
        </p>
    </body>
    </html>
    """
    
    return html

def enviar_relatorio():
    """Envia relatório por email"""
    
    html = gerar_html_relatorio()
    
    msg = EmailMessage()
    msg['Subject'] = f'📊 Relatório Semanal - {datetime.now().strftime("%d/%m/%Y")}'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO
    
    msg.set_content("Relatório em anexo. Ative o HTML para visualizar.")
    msg.add_alternative(html, subtype='html')
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
        print("✅ Relatório enviado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    enviar_relatorio()