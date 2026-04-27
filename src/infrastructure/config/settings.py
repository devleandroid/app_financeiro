"""Configurações da aplicação"""
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

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
    
    # Admin
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_PASS") 
    
    # Database - Usar DATABASE_URL do Koyeb
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # Se não tiver DATABASE_URL, usa SQLite local
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///acessos.db"
        logger.info("📁 Usando SQLite local")
    else:
        logger.info(f"🐘 Usando PostgreSQL: {DATABASE_URL[:50]}...")
    
    # APIs externas
    FIXER_API_KEY = os.getenv("FIXER_API_KEY", "")
    CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY", "")
    
    # Email
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVIDOR", "smtp.gmail.com")
    SMTP_PORTA = int(os.getenv("SMTP_PORTA", "587"))

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Plataforma de Sites - Regras de Negocio
    FREE_SITES_LIMIT = 2
    PRO_SITES_LIMIT = 10
    EXTRA_SITE_PRICE = 399.90
    MAX_SITES_PER_USER = 30
    PRO_PLAN_PRICE = 69.90

    # Pagamento
    PAYMENT_GATEWAY = os.getenv("PAYMENT_GATEWAY", "mercadopago")
    MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

    # Paths
    GENERATED_SITES_DIR = str(Path(__file__).parent.parent.parent.parent / "generated_sites")
    TEMPLATES_DIR = str(Path(__file__).parent.parent.parent / "presentation" / "web" / "templates")

    @property
    def is_development(self):
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self):
        return self.ENVIRONMENT == "production"

# Instância global
settings = Settings()
