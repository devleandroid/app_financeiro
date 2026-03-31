"""Endpoint de debug para verificar variáveis de ambiente"""
from fastapi import APIRouter, Depends, HTTPException
import os
import secrets

router = APIRouter(prefix="/debug", tags=["debug"])

# Autenticação básica para debug
from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica credenciais do admin"""
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASSWORD") or "admin123"
    
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
        "FIXER_API_KEY": "✅ Configurado" if os.getenv("FIXER_API_KEY") else "❌ Não configurado",
        "EMAIL_REMETENTE": "✅ Configurado" if os.getenv("EMAIL_REMETENTE") else "⚠️ Opcional",
    }
    return {
        "status": "ok",
        "service": "investsmart-backend",
        "variaveis": vars_status,
        "raw": {
            "ADMIN_USER": os.getenv("ADMIN_USER"),
            "ADMIN_PASSWORD": "***" if os.getenv("ADMIN_PASSWORD") else None,
        }
    }