"""Router para servir as paginas HTML do frontend."""
import os
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

from src.infrastructure.config.settings import settings
from src.infrastructure.database import site_repository_sqlite as repo

router = APIRouter(tags=["Paginas Web"])

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "web" / "templates"


def _read_template(filename: str) -> str:
    filepath = TEMPLATES_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/", response_class=HTMLResponse)
async def home_page():
    """Pagina inicial (landing page) da plataforma."""
    return HTMLResponse(content=_read_template("index.html"))


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Pagina de login."""
    return HTMLResponse(content=_read_template("login.html"))


@router.get("/register", response_class=HTMLResponse)
async def register_page():
    """Pagina de cadastro."""
    return HTMLResponse(content=_read_template("register.html"))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Pagina do dashboard do usuario."""
    return HTMLResponse(content=_read_template("dashboard.html"))


@router.get("/create-site", response_class=HTMLResponse)
async def create_site_page():
    """Pagina de criacao de site."""
    return HTMLResponse(content=_read_template("create_site.html"))


@router.get("/plans", response_class=HTMLResponse)
async def plans_page():
    """Pagina de planos e precos."""
    return HTMLResponse(content=_read_template("plans.html"))


@router.get("/site/{slug}", response_class=HTMLResponse)
async def view_published_site(slug: str):
    """
    Exibe um site publicado pelo slug.
    Primeiro tenta servir do banco, depois de arquivo.
    """
    site = repo.buscar_site_por_slug(slug)
    if not site:
        return HTMLResponse(
            content="<h1>Site nao encontrado</h1><p><a href='/'>Voltar</a></p>",
            status_code=404
        )

    if site.get("html_gerado"):
        return HTMLResponse(content=site["html_gerado"])

    # Tentar ler do arquivo
    html_path = os.path.join(settings.GENERATED_SITES_DIR, f"{slug}.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return HTMLResponse(
        content="<h1>Site nao disponivel</h1><p><a href='/'>Voltar</a></p>",
        status_code=404
    )
