# Ponto de entrada da API FastAPI"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.infrastructure.config.settings import settings
from src.infrastructure.config.logging import setup_logging

# Importar routers
from src.presentation.api.routers import public
from src.presentation.api.routers import admin
from src.presentation.api.routers import investment

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para análise de investimentos",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers - TODOS os endpoints estarão disponíveis
app.include_router(public.router, prefix="/api")
app.include_router(investment.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "endpoints": {
            "public": "/api/health, /api/ping, /api/solicitar-chave, /api/validar-chave",
            "investment": "/api/investment/dados, /api/investment/recomendacoes",
            "admin": "/api/admin/solicitacoes, /api/admin/acessos (protegido)"
        }
    }

@app.get("/api")
async def api_root():
    """Rota raiz da API"""
    return {
        "mensagem": "Bem-vindo à API do InvestSmart",
        "documentacao": "/docs",
        "versao": settings.VERSION
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 API iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 API encerrada")