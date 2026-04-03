"""Endpoint de debug para verificar variáveis de ambiente"""
from fastapi import APIRouter, Depends, HTTPException
import os
import logging

router = APIRouter(prefix="/debug", tags=["debug"])
logger = logging.getLogger(__name__)

# Autenticação básica para debug (protegido)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica credenciais do admin"""
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_PASS") or "admin123"
    
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@router.get("/env")
async def get_env_vars(admin: str = Depends(verify_admin)):
    """Retorna status das variáveis de ambiente (apenas para admin)"""
    vars_status = {
        "ADMIN_USER": os.getenv("ADMIN_USER", "NÃO CONFIGURADO"),
        "ADMIN_PASSWORD": "✅ Configurado" if os.getenv("ADMIN_PASSWORD") else "❌ Não configurado",
        "ADMIN_PASS": "✅ Configurado" if os.getenv("ADMIN_PASS") else "❌ Não configurado",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "NÃO CONFIGURADO"),
        "API_URL": os.getenv("API_URL", "NÃO CONFIGURADO"),
        "KOYEB_PUBLIC_DOMAIN": os.getenv("KOYEB_PUBLIC_DOMAIN", "N/A"),
        "PORT": os.getenv("PORT", "N/A"),
    }
    
    # Log apenas para debug
    logger.info(f"Debug endpoint acessado por {admin}")
    
    return {
        "status": "ok",
        "service": "investsmart-backend",
        "variaveis": vars_status
    }

@router.get("/simple")
async def simple_debug():
    """Endpoint simples sem autenticação (apenas informações não sensíveis)"""
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "koyeb_domain": os.getenv("KOYEB_PUBLIC_DOMAIN", "N/A"),
    }