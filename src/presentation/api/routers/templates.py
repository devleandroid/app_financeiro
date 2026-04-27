"""Router de templates disponiveis."""
from fastapi import APIRouter

from src.infrastructure.database import site_repository_sqlite as repo

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("")
async def listar_templates():
    """Lista todos os templates disponiveis para criacao de sites."""
    templates = repo.listar_templates()
    return {"success": True, "templates": templates}


@router.get("/{template_id}")
async def obter_template(template_id: str):
    """Retorna detalhes de um template especifico."""
    template = repo.buscar_template(template_id)
    if not template:
        return {"success": False, "detail": "Template nao encontrado"}
    return {"success": True, "template": template}
