"""Middleware para limitar tentativas de login"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita tentativas de acesso por IP"""
    
    def __init__(self, app, max_attempts: int = 5, window_seconds: int = 300):
        super().__init__(app)
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Aplicar rate limit apenas para endpoints de admin
        if "/api/admin" in request.url.path:
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            
            # Limpar tentativas antigas
            self.attempts[client_ip] = [
                t for t in self.attempts[client_ip] 
                if now - t < self.window_seconds
            ]
            
            # Verificar limite
            if len(self.attempts[client_ip]) >= self.max_attempts:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas tentativas. Aguarde 5 minutos."}
                )
            
            # Registrar tentativa (apenas para endpoints autenticados)
            # Verificar se é uma tentativa de login (requisição com auth)
            if request.headers.get("authorization"):
                self.attempts[client_ip].append(now)
        
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Registrar tentativa falha para rate limit
            if "/api/admin" in request.url.path and e.status_code == 401:
                client_ip = request.client.host if request.client else "unknown"
                self.attempts[client_ip].append(time.time())
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Erro no middleware: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro interno do servidor"}
            )
