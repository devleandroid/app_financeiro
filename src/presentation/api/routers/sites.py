"""Router de sites - CRUD, preview, publicacao."""
import re
import unicodedata
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.auth.jwt_auth import get_current_user
from src.infrastructure.database import site_repository_sqlite as repo
from src.application.services.site_generator import gerar_html_site, salvar_site_html
from src.application.services.plan_service import verificar_pode_criar_site

router = APIRouter(prefix="/sites", tags=["Sites"])


class CreateSiteRequest(BaseModel):
    nome_negocio: str
    descricao: Optional[str] = ""
    segmento: Optional[str] = ""
    telefone: Optional[str] = ""
    whatsapp: Optional[str] = ""
    email_contato: Optional[str] = ""
    endereco: Optional[str] = ""
    template_id: str = "restaurante"
    cor_primaria: Optional[str] = "#2563eb"
    cor_secundaria: Optional[str] = "#1e1e2e"
    cor_texto: Optional[str] = "#ffffff"
    logo_url: Optional[str] = ""
    fotos: Optional[list] = []
    redes_sociais: Optional[dict] = {}


class UpdateSiteRequest(BaseModel):
    nome_negocio: Optional[str] = None
    descricao: Optional[str] = None
    segmento: Optional[str] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    email_contato: Optional[str] = None
    endereco: Optional[str] = None
    template_id: Optional[str] = None
    cor_primaria: Optional[str] = None
    cor_secundaria: Optional[str] = None
    cor_texto: Optional[str] = None
    logo_url: Optional[str] = None
    fotos: Optional[list] = None
    redes_sociais: Optional[dict] = None


def _gerar_slug(nome: str) -> str:
    """Gera um slug URL-friendly a partir do nome do negocio."""
    nfkd = unicodedata.normalize('NFKD', nome.lower())
    ascii_text = nfkd.encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '-', ascii_text).strip('-')
    if not slug:
        slug = "meu-site"
    existing = repo.buscar_site_por_slug(slug)
    if existing:
        counter = 1
        while repo.buscar_site_por_slug(f"{slug}-{counter}"):
            counter += 1
        slug = f"{slug}-{counter}"
    return slug


@router.get("")
async def listar_sites(user: dict = Depends(get_current_user)):
    """Lista todos os sites do usuario logado."""
    sites = repo.listar_sites_usuario(user["id"])
    return {"success": True, "sites": sites, "total": len(sites)}


@router.post("")
async def criar_site(req: CreateSiteRequest, user: dict = Depends(get_current_user)):
    """
    Cria um novo site.

    Verifica os limites do plano antes de criar:
    - FREE: ate 2 sites
    - PRO: ate 10 sites
    - Apos 10: R$399,90 por site extra (max 30)
    """
    if not req.nome_negocio.strip():
        raise HTTPException(status_code=400, detail="O nome do negocio e obrigatorio")

    # Verificar limites do plano
    check = verificar_pode_criar_site(user["id"])
    if not check["pode_criar"]:
        raise HTTPException(status_code=403, detail=check["motivo"])

    # Gerar slug unico
    slug = _gerar_slug(req.nome_negocio)

    # Preparar dados
    dados = req.model_dump()
    dados["slug"] = slug

    # Criar no banco
    site = repo.criar_site(user["id"], dados)

    # Gerar HTML
    html = gerar_html_site(dados)
    repo.atualizar_site(site["id"], {"html_gerado": html})

    # Informar se precisa pagar extra
    response = {
        "success": True,
        "site": site,
        "slug": slug,
        "preview_url": f"/api/sites/{site['id']}/preview",
    }

    if check.get("precisa_pagar_extra"):
        response["aviso"] = f"Este site requer pagamento adicional de R${check['valor_extra']:.2f}"
        response["valor_extra"] = check["valor_extra"]

    return response


@router.get("/check-limit")
async def verificar_limite(user: dict = Depends(get_current_user)):
    """Verifica se o usuario pode criar mais sites."""
    check = verificar_pode_criar_site(user["id"])
    return {"success": True, **check}


@router.get("/{site_id}")
async def obter_site(site_id: int, user: dict = Depends(get_current_user)):
    """Retorna detalhes de um site especifico."""
    site = repo.buscar_site_por_id(site_id)
    if not site or site["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Site nao encontrado")
    return {"success": True, "site": site}


@router.put("/{site_id}")
async def atualizar_site(site_id: int, req: UpdateSiteRequest,
                         user: dict = Depends(get_current_user)):
    """Atualiza dados de um site existente."""
    site = repo.buscar_site_por_id(site_id)
    if not site or site["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Site nao encontrado")

    dados = {k: v for k, v in req.model_dump().items() if v is not None}
    site_atualizado = repo.atualizar_site(site_id, dados)

    # Regenerar HTML com dados atualizados
    site_completo = repo.buscar_site_por_id(site_id)
    html = gerar_html_site(site_completo)
    repo.atualizar_site(site_id, {"html_gerado": html})

    return {"success": True, "site": site_atualizado}


@router.delete("/{site_id}")
async def deletar_site(site_id: int, user: dict = Depends(get_current_user)):
    """Deleta um site."""
    site = repo.buscar_site_por_id(site_id)
    if not site or site["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Site nao encontrado")

    success = repo.deletar_site(site_id, user["id"])
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao deletar site")

    return {"success": True, "message": "Site deletado com sucesso"}


@router.get("/{site_id}/preview", response_class=HTMLResponse)
async def preview_site(site_id: int):
    """
    Retorna o preview do site em HTML.
    Nao requer autenticacao para permitir compartilhamento.
    """
    site = repo.buscar_site_por_id(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site nao encontrado")

    if site.get("html_gerado"):
        return HTMLResponse(content=site["html_gerado"])

    # Gerar HTML on-the-fly
    html = gerar_html_site(site)
    return HTMLResponse(content=html)


@router.post("/{site_id}/publish")
async def publicar_site(site_id: int, user: dict = Depends(get_current_user)):
    """
    Publica um site, tornando-o acessivel via slug.

    Requer plano PRO para publicar.
    """
    site = repo.buscar_site_por_id(site_id)
    if not site or site["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Site nao encontrado")

    if user["plano"] == "free":
        raise HTTPException(
            status_code=403,
            detail="Para publicar sites, voce precisa assinar o plano Pro (R$69,90/mes)"
        )

    # Gerar e salvar HTML
    html = gerar_html_site(site)
    salvar_site_html(site["slug"], html)

    # Atualizar status
    repo.atualizar_site(site_id, {
        "status": "publicado",
        "html_gerado": html,
        "site_url": f"/site/{site['slug']}"
    })

    return {
        "success": True,
        "message": "Site publicado com sucesso!",
        "url": f"/site/{site['slug']}",
        "slug": site["slug"]
    }
