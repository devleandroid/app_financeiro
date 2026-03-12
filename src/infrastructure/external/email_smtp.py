# Serviço de envio de email via SMTP"""
import smtplib
import os
from email.message import EmailMessage
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """Implementação do envio de email usando SMTP"""
    
    def __init__(self):
        from src.infrastructure.config.settings import settings
        self.smtp_server = settings.SMTP_SERVIDOR
        self.smtp_port = settings.SMTP_PORTA
        self.username = settings.EMAIL_REMETENTE
        self.password = settings.EMAIL_SENHA
        
        # Modo debug - mostra configurações sem enviar
        logger.info(f"📧 Configurações de email:")
        logger.info(f"   Servidor: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"   Usuário: {self.username}")
        logger.info(f"   Senha: {'Configurada' if self.password else 'NÃO CONFIGURADA'}")
    
    def send_key(self, to_email: str, key: str) -> bool:
        """Envia uma chave de acesso por email"""
        
        # Se não tiver configurações, mostra no console (modo desenvolvimento)
        if not self.username or not self.password:
            logger.warning("⚠️ Email não configurado. Mostrando chave no console:")
            print(f"\n{'='*60}")
            print(f"📧 PARA: {to_email}")
            print(f"🔑 CHAVE: {key}")
            print(f"⏰ VÁLIDA POR: 4 horas")
            print(f"{'='*60}\n")
            return True
        
        try:
            # Criar mensagem
            msg = EmailMessage()
            msg['Subject'] = "🔑 Sua chave de acesso - InvestSmart"
            msg['From'] = self.username
            msg['To'] = to_email
            
            # Corpo em texto plano
            text_body = f"""
            Olá!
            
            Sua chave de acesso ao InvestSmart é: {key}
            
            Esta chave é válida por 4 horas.
            
            Acesse: http://localhost:8501 e digite sua chave.
            
            Atenciosamente,
            Equipe InvestSmart
            """
            
            # Corpo em HTML
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4361ee; color: white; padding: 20px; text-align: center; }}
                    .chave {{ 
                        background: #f8f9fa; 
                        padding: 20px; 
                        text-align: center; 
                        font-size: 32px; 
                        font-weight: bold;
                        letter-spacing: 5px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💰 InvestSmart</h1>
                    </div>
                    <p>Olá,</p>
                    <p>Sua chave de acesso ao InvestSmart é:</p>
                    <div class="chave">{key}</div>
                    <p>Esta chave é válida por <strong>4 horas</strong>.</p>
                    <p>Acesse o link abaixo e digite sua chave:</p>
                    <p><a href="http://localhost:8501">http://localhost:8501</a></p>
                    <hr>
                    <p style="color: gray;">Atenciosamente,<br>Equipe InvestSmart</p>
                </div>
            </body>
            </html>
            """
            
            msg.set_content(text_body)
            msg.add_alternative(html_body, subtype='html')
            
            # Enviar
            logger.info(f"📤 Enviando email para {to_email}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado com sucesso para {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Erro de autenticação SMTP. Verifique usuário/senha.")
            print("\n🔐 DICA: Se estiver usando Gmail, use uma 'Senha de App' em:")
            print("   https://myaccount.google.com/apppasswords")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            return False