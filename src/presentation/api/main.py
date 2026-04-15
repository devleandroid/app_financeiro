"""Ponto de entrada da API FastAPI"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.infrastructure.config.settings import settings
from src.infrastructure.config.logging import setup_logging

# Importar routers
from src.presentation.api.routers import public
from src.presentation.api.routers import admin
from src.presentation.api.routers import investment
from src.presentation.api.routers import debug
from src.presentation.api.routers import health

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================
# CRIAR APP FASTAPI (PRIMEIRO!)
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    description="API para análise de investimentos",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# ============================================
# ADICIONAR MIDDLEWARES (DEPOIS DO APP!)
# ============================================

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Rate Limiting (proteção contra força bruta)
try:
    from src.presentation.api.middlewares.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware, max_attempts=5, window_seconds=300)
    logger.info("✅ Rate limiting middleware carregado")
except ImportError as e:
    logger.warning(f"⚠️ Rate limiting middleware não disponível: {e}")

# ============================================
# INCLUIR ROUTERS
# ============================================
app.include_router(health.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(investment.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(debug.router, prefix="/api")

# ============================================
# ENDPOINTS BÁSICOS
# ============================================
@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT
    }

@app.get("/api")
async def api_root():
    """Rota raiz da API"""
    return {
        "mensagem": "Bem-vindo à API do InvestSmart",
        "documentacao": "/docs",
        "versao": settings.VERSION
    }

# ============================================
# EVENTOS DE STARTUP/SHUTDOWN
# ============================================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 API iniciada com sucesso!")
    logger.info(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"👤 Admin User: {settings.ADMIN_USER}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 API encerrada")
