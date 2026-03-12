"""Configurações da aplicação"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    """Classe de configurações"""
    
    # Configurações da aplicação
    APP_NAME = "InvestSmart"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # URLs
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:8501",
        "http://localhost:8502",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
    ]
    
    # Admin
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
    
    # APIs externas
    FIXER_API_KEY = os.getenv("FIXER_API_KEY", "")
    
    # Email
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVIDOR", "smtp.gmail.com")
    SMTP_PORTA = int(os.getenv("SMTP_PORTA", "587"))
    
    # Banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "acessos.db")

# Instância global
settings = Settings()