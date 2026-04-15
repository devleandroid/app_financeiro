"""Middleware para limitar tentativas de login"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita tentativas de login por IP"""
    
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
                raise HTTPException(
                    status_code=429,
                    detail="Muitas tentativas. Aguarde 5 minutos."
                )
            
            # Registrar tentativa
            self.attempts[client_ip].append(now)
        
        response = await call_next(request)
        return response
