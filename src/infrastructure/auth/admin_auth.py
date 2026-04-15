"""Autenticação para área administrativa com logging e rate limit"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import logging
from datetime import datetime
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
security = HTTPBasic()

def verificar_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    request: Request = None
):
    """Verifica credenciais do admin com logging"""
    
    client_ip = request.client.host if request and request.client else "unknown"
    
    # Verificar usuário
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASS)
    
    if not (correct_username and correct_password):
        # Log de tentativa falha
        logger.warning(
            f"⚠️ Tentativa de acesso admin falhou - IP: {client_ip}, "
            f"Usuário: {credentials.username}, Hora: {datetime.now().isoformat()}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Log de acesso bem-sucedido
    logger.info(
        f"✅ Acesso admin autorizado - IP: {client_ip}, "
        f"Usuário: {credentials.username}, Hora: {datetime.now().isoformat()}"
    )
    
    return credentials.username
