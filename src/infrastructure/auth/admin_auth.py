"""Autenticação para área administrativa"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from src.infrastructure.config.settings import settings

security = HTTPBasic()

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica se as credenciais são do admin"""
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASS)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username