# email_service.py
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.remetente = os.getenv("EMAIL_REMETENTE")
        self.senha = os.getenv("EMAIL_SENHA")
        self.smtp_server = os.getenv("SMTP_SERVIDOR", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORTA", "587"))
        
        if not self.remetente or not self.senha:
            print("⚠️ Configurações de email incompletas. Verifique o arquivo .env")
    
    def enviar_chave_acesso(self, email_destino: str, chave: str, horas_validade: int = 4) -> bool:
        """
        Envia email com a chave de acesso
        """
        if not self.remetente or not self.senha:
            print("❌ Email não configurado. Imprimindo chave no console para teste.")
            print(f"\n{'='*50}")
            print(f"📧 PARA: {email_destino}")
            print(f"🔑 CHAVE: {chave}")
            print(f"⏰ VÁLIDA POR: {horas_validade} horas")
            print(f"{'='*50}\n")
            return True
        
        assunto = "🔑 Sua chave de acesso - InvestSmart"
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background: linear-gradient(135deg, #4361ee, #3f37c9);
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{ 
                    background: #f8f9fa; 
                    padding: 30px; 
                    border-radius: 0 0 10px 10px;
                }}
                .chave-container {{ 
                    background: white; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 32px; 
                    font-weight: bold;
                    letter-spacing: 8px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border: 2px dashed #4361ee;
                }}
                .validade {{ 
                    color: #f72585; 
                    font-weight: bold;
                    text-align: center;
                    font-size: 18px;
                    margin: 20px 0;
                }}
                .instrucoes {{ 
                    background: #e9ecef; 
                    padding: 20px; 
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .footer {{ 
                    text-align: center; 
                    color: #6c757d; 
                    font-size: 0.8em;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 InvestSmart</h1>
                    <p>Plataforma de Análise de Investimentos</p>
                </div>
                
                <div class="content">
                    <h2>Olá!</h2>
                    
                    <p>Você solicitou acesso ao InvestSmart. Utilize a chave abaixo para entrar no sistema:</p>
                    
                    <div class="chave-container">
                        {chave}
                    </div>
                    
                    <div class="validade">
                        ⏰ Esta chave expira em <strong>{horas_validade} horas</strong>
                    </div>
                    
                    <div class="instrucoes">
                        <h3>📋 Instruções:</h3>
                        <ol>
                            <li>Volte ao site do InvestSmart</li>
                            <li>Na aba "Já tenho chave", digite o código acima</li>
                            <li>Você será redirecionado ao dashboard</li>
                            <li>A chave expira automaticamente após {horas_validade} horas</li>
                        </ol>
                    </div>
                    
                    <p><strong>Importante:</strong> Não compartilhe esta chave com ninguém. Cada chave é única e pessoal.</p>
                    
                    <div class="footer">
                        <p>Se não foi você que solicitou, ignore este email.</p>
                        <p>© 2024 InvestSmart - Todos os direitos reservados</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        corpo_texto = f"""
        Sua chave de acesso ao InvestSmart é: {chave}
        
        Esta chave expira em {horas_validade} horas.
        
        Instruções:
        1. Volte ao site do InvestSmart
        2. Digite a chave: {chave}
        3. Acesse o dashboard
        
        Se não foi você que solicitou, ignore este email.
        """
        
        try:
            msg = EmailMessage()
            msg['Subject'] = assunto
            msg['From'] = self.remetente
            msg['To'] = email_destino
            msg.set_content(corpo_texto)
            msg.add_alternative(corpo_html, subtype='html')
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.remetente, self.senha)
                server.send_message(msg)
            
            print(f"✅ Email enviado para {email_destino}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            print(f"\n{'='*50}")
            print(f"📧 PARA: {email_destino}")
            print(f"🔑 CHAVE: {chave}")
            print(f"⏰ VÁLIDA POR: {horas_validade} horas")
            print(f"{'='*50}\n")
            return False

# Instância global
email_service = EmailService()