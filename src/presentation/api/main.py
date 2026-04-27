"""Ponto de entrada da API FastAPI - SitesPro + InvestSmart"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from src.infrastructure.config.settings import settings
from src.infrastructure.config.logging import setup_logging

# Importar routers existentes
from src.presentation.api.routers import public
from src.presentation.api.routers import admin
from src.presentation.api.routers import investment
from src.presentation.api.routers import debug
from src.presentation.api.routers import health

# Importar novos routers da plataforma de sites
from src.presentation.api.routers import auth
from src.presentation.api.routers import sites
from src.presentation.api.routers import subscriptions
from src.presentation.api.routers import templates
from src.presentation.api.routers import web_pages

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================
# CRIAR APP FASTAPI
# ============================================
app = FastAPI(
    title="SitesPro",
    description="Plataforma de criacao de sites profissionais + API de investimentos",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# ============================================
# ARQUIVOS ESTATICOS
# ============================================
static_dir = Path(__file__).parent.parent / "web" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ============================================
# ADICIONAR MIDDLEWARES
# ============================================

# Middleware de CORS
cors_origins = settings.CORS_ORIGINS + [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# INCLUIR ROUTERS - API
# ============================================
# Routers existentes
app.include_router(health.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(investment.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(debug.router, prefix="/api")

# Novos routers - Plataforma de Sites
app.include_router(auth.router, prefix="/api")
app.include_router(sites.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(templates.router, prefix="/api")

# ============================================
# INCLUIR ROUTERS - PAGINAS WEB
# ============================================
app.include_router(web_pages.router)

# ============================================
# ENDPOINTS BASICOS
# ============================================
@app.get("/api")
async def api_root():
    """Rota raiz da API"""
    return {
        "app": "SitesPro",
        "mensagem": "Bem-vindo a API SitesPro",
        "documentacao": "/docs",
        "versao": settings.VERSION,
        "modulos": ["sites", "investimentos", "admin"]
    }

# ============================================
# EVENTOS DE STARTUP/SHUTDOWN
# ============================================
@app.on_event("startup")
async def startup_event():
    # Criar tabelas do banco de dados se nao existirem
    from src.infrastructure.database.migrations.criar_tabelas_sites import criar_tabelas
    try:
        criar_tabelas()
        logger.info("Banco de dados da plataforma de sites inicializado")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")

    logger.info("API SitesPro iniciada com sucesso!")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API SitesPro encerrada")
