# Rotas administrativas (protegidas)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from src.infrastructure.auth.admin_auth import verificar_admin
from src.infrastructure.database.unified_repository import admin_repo
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/solicitacoes")
async def get_solicitacoes(
    limite: int = Query(100, ge=1, le=1000),
    pagina: int = Query(1, ge=1),
    admin: str = Depends(verificar_admin)
):
    """Retorna solicitações de chave reais"""
    try:
        logger.info(f"👤 Admin {admin} acessou solicitações (página {pagina})")
        
        offset = (pagina - 1) * limite
        solicitacoes = admin_repo.get_solicitacoes(limite=limite, offset=offset)
        
        return {
            "sucesso": True,
            "dados": solicitacoes,
            "pagina": pagina,
            "limite": limite,
            "total": len(solicitacoes)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar solicitações: {e}")
        return {"sucesso": False, "erro": str(e)}

@router.get("/acessos")
async def get_acessos(
    limite: int = Query(100, ge=1, le=1000),
    pagina: int = Query(1, ge=1),
    admin: str = Depends(verificar_admin)
):
    """Retorna acessos reais ao dashboard"""
    try:
        logger.info(f"👤 Admin {admin} acessou relatório de acessos (página {pagina})")
        
        offset = (pagina - 1) * limite
        acessos = admin_repo.get_acessos(limite=limite, offset=offset)
        
        return {
            "sucesso": True,
            "dados": acessos,
            "pagina": pagina,
            "limite": limite,
            "total": len(acessos)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar acessos: {e}")
        return {"sucesso": False, "erro": str(e)}

@router.get("/estatisticas")
async def get_estatisticas(admin: str = Depends(verificar_admin)):
    """Retorna estatísticas reais do sistema"""
    try:
        logger.info(f"👤 Admin {admin} acessou estatísticas")
        
        stats = admin_repo.get_estatisticas()
        
        return {
            "sucesso": True,
            "estatisticas": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return {"sucesso": False, "erro": str(e)}

@router.get("/atividades")
async def get_atividades(
    limite: int = Query(20, ge=1, le=100),
    admin: str = Depends(verificar_admin)
):
    """Retorna últimas atividades do sistema"""
    try:
        logger.info(f"👤 Admin {admin} acessou últimas atividades")
        
        atividades = admin_repo.get_ultimas_atividades(limite=limite)
        
        return {
            "sucesso": True,
            "atividades": atividades,
            "total": len(atividades)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar atividades: {e}")
        return {"sucesso": False, "erro": str(e)}