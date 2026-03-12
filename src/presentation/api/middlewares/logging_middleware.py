import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
import json
from typing import Callable
import sys
sys.path.append('..')
from logging_config import get_logger

# Loggers
access_logger = get_logger('access')
app_logger = get_logger('app')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logar todas as requisições e respostas [citation:3][citation:8]
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Início da requisição
        start_time = time.time()
        
        # Obter IP do cliente (considerando proxies)
        client_ip = request.headers.get('x-forwarded-for', 
                                       request.client.host if request.client else 'unknown')
        
        # Log da requisição (início)
        req_body = await self._get_request_body(request)
        
        # Processar a requisição
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log da resposta
            await self._log_response(request, response, client_ip, process_time, req_body)
            
            # Adicionar header com tempo de processamento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as exc:
            # Log de erro
            process_time = time.time() - start_time
            self._log_error(request, exc, client_ip, process_time)
            raise
    
    async def _get_request_body(self, request: Request) -> dict:
        """Extrai e mascara dados sensíveis do corpo da requisição [citation:3]"""
        try:
            body = await request.body()
            if body:
                # Tentar parsear como JSON
                try:
                    data = json.loads(body)
                    # Mascarar dados sensíveis
                    return self._mask_sensitive_data(data)
                except:
                    return {"raw": body.decode('utf-8', errors='ignore')[:500]}
        except:
            return {}
        return {}
    
    def _mask_sensitive_data(self, data):
        """Mascara campos sensíveis como senhas, tokens [citation:3]"""
        sensitive_keys = {'password', 'token', 'api_key', 'secret', 
                         'authorization', 'jwt', 'access_token'}
        
        if isinstance(data, dict):
            return {
                k: ('******' if k.lower() in sensitive_keys else self._mask_sensitive_data(v))
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data
    
    async def _log_response(self, request: Request, response: Response, 
                           client_ip: str, process_time: float, req_body: dict):
        """Loga detalhes da resposta"""
        extra = {
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'status_code': response.status_code,
            'client_ip': client_ip,
            'user_agent': request.headers.get('user-agent', 'unknown'),
            'process_time': round(process_time, 3),
            'request_body': req_body if req_body else None
        }
        
        # Se houver autenticação, tentar pegar usuário
        if hasattr(request.state, 'user'):
            extra['user'] = request.state.user
        
        access_logger.info(f"Request completed", extra=extra)
    
    def _log_error(self, request: Request, exc: Exception, 
                   client_ip: str, process_time: float):
        """Loga erros"""
        error_logger = get_logger('error')
        extra = {
            'method': request.method,
            'path': request.url.path,
            'client_ip': client_ip,
            'process_time': round(process_time, 3),
            'error_type': type(exc).__name__
        }
        error_logger.error(f"Request failed: {str(exc)}", extra=extra)

# Para usar no main.py:
# app.add_middleware(RequestLoggingMiddleware)
