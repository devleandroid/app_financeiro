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
        "https://*.streamlit.app",
        "https://*.koyeb.app"
    ]
    
    # Admin - usa a variável correta do Koyeb
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    # Lê ADMIN_PASSWORD primeiro (Koyeb), depois ADMIN_PASS (local)
    admin_password_env = os.getenv("ADMIN_PASSWORD", "")
    admin_pass_env = os.getenv("ADMIN_PASS", "")

    # LOG CRÍTICO PARA DEBUG
    logger.info("=" * 50)
    logger.info("🔍 DEBUG DE CONFIGURAÇÃO DO ADMIN")
    logger.info("=" * 50)
    logger.info(f"ADMIN_PASSWORD from env: '{admin_password_env}'")
    logger.info(f"ADMIN_PASS from env: '{admin_pass_env}'")
    logger.info(f"ADMIN_USER from env: '{ADMIN_USER}'")
    
    # Definir a senha final
    if admin_password_env:
        ADMIN_PASS = admin_password_env
        logger.info(f"✅ Usando ADMIN_PASSWORD: '{admin_password_env[:4]}***'")
    elif admin_pass_env:
        ADMIN_PASS = admin_pass_env
        logger.info(f"✅ Usando ADMIN_PASS: '{admin_pass_env[:4]}***'")
    else:
        ADMIN_PASS = ""  # Sem fallback
        logger.warning("⚠️ NENHUMA SENHA CONFIGURADA! Painel admin não acessível.")
    
    logger.info(f"ADMIN_PASS final: {'*' * len(ADMIN_PASS) if ADMIN_PASS else 'VAZIO'}")
    logger.info("=" * 50)
    
    # APIs externas
    FIXER_API_KEY = os.getenv("FIXER_API_KEY", "")
    CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY", "")
    
    # Email
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVIDOR", "smtp.gmail.com")
    SMTP_PORTA = int(os.getenv("SMTP_PORTA", "587"))
    
    # Banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "acessos.db")
    
    @property
    def is_development(self):
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self):
        return self.ENVIRONMENT == "production"

# Instância global
settings = Settings()
