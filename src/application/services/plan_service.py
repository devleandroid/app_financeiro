"""
Servico de gerenciamento de planos e limites.

Regras de negocio:
- Plano FREE: ate 2 sites gratuitos
- Plano PRO (R$69,90/mes): ate 10 sites no total (inclui os 2 gratis)
- Site extra alem dos 10: R$399,90 por site
- Maximo absoluto: 30 sites por usuario
- Busca de prospeccao: ilimitada para todos
"""
import logging
from typing import Optional

from src.infrastructure.config.settings import settings
from src.infrastructure.database import site_repository_sqlite as repo

logger = logging.getLogger(__name__)


class PlanError(Exception):
    """Erro relacionado a regras de plano."""
    pass


def verificar_pode_criar_site(user_id: int) -> dict:
    """
    Verifica se o usuario pode criar um novo site.

    Retorna um dict com:
        - pode_criar: bool
        - motivo: str (se nao puder)
        - precisa_pagar_extra: bool
        - valor_extra: float (se precisar pagar)
        - plano_atual: str
        - sites_criados: int
        - limite_atual: int
    """
    user = repo.buscar_usuario_por_id(user_id)
    if not user:
        raise PlanError("Usuario nao encontrado")

    sites_criados = repo.contar_sites_usuario(user_id)
    plano = user["plano"]

    # Limite absoluto: 30 sites
    if sites_criados >= settings.MAX_SITES_PER_USER:
        return {
            "pode_criar": False,
            "motivo": f"Limite maximo de {settings.MAX_SITES_PER_USER} sites atingido",
            "precisa_pagar_extra": False,
            "valor_extra": 0,
            "plano_atual": plano,
            "sites_criados": sites_criados,
            "limite_atual": settings.MAX_SITES_PER_USER
        }

    # Plano FREE: limite de 2 sites
    if plano == "free":
        if sites_criados >= settings.FREE_SITES_LIMIT:
            return {
                "pode_criar": False,
                "motivo": f"Voce atingiu o limite de {settings.FREE_SITES_LIMIT} sites gratuitos. Assine o plano Pro por R${settings.PRO_PLAN_PRICE:.2f}/mes para criar ate {settings.PRO_SITES_LIMIT} sites.",
                "precisa_pagar_extra": False,
                "precisa_assinar": True,
                "valor_plano": settings.PRO_PLAN_PRICE,
                "plano_atual": plano,
                "sites_criados": sites_criados,
                "limite_atual": settings.FREE_SITES_LIMIT
            }
        return {
            "pode_criar": True,
            "motivo": "",
            "precisa_pagar_extra": False,
            "plano_atual": plano,
            "sites_criados": sites_criados,
            "limite_atual": settings.FREE_SITES_LIMIT,
            "sites_restantes": settings.FREE_SITES_LIMIT - sites_criados
        }

    # Plano PRO: limite de 10 sites
    if plano == "pro":
        if sites_criados >= settings.PRO_SITES_LIMIT:
            return {
                "pode_criar": True,
                "motivo": f"Voce atingiu o limite do plano Pro ({settings.PRO_SITES_LIMIT} sites). O proximo site custara R${settings.EXTRA_SITE_PRICE:.2f}.",
                "precisa_pagar_extra": True,
                "valor_extra": settings.EXTRA_SITE_PRICE,
                "plano_atual": plano,
                "sites_criados": sites_criados,
                "limite_atual": settings.PRO_SITES_LIMIT
            }
        return {
            "pode_criar": True,
            "motivo": "",
            "precisa_pagar_extra": False,
            "plano_atual": plano,
            "sites_criados": sites_criados,
            "limite_atual": settings.PRO_SITES_LIMIT,
            "sites_restantes": settings.PRO_SITES_LIMIT - sites_criados
        }

    return {
        "pode_criar": True,
        "motivo": "",
        "precisa_pagar_extra": False,
        "plano_atual": plano,
        "sites_criados": sites_criados,
        "limite_atual": settings.PRO_SITES_LIMIT
    }


def obter_info_plano(user_id: int) -> dict:
    """Retorna informacoes completas sobre o plano do usuario."""
    user = repo.buscar_usuario_por_id(user_id)
    if not user:
        raise PlanError("Usuario nao encontrado")

    sites_criados = repo.contar_sites_usuario(user_id)
    plano = user["plano"]
    assinatura = repo.buscar_assinatura_ativa(user_id)

    if plano == "free":
        limite = settings.FREE_SITES_LIMIT
    else:
        limite = settings.PRO_SITES_LIMIT

    return {
        "plano": plano,
        "sites_criados": sites_criados,
        "limite_sites": limite,
        "sites_restantes_no_plano": max(0, limite - sites_criados),
        "maximo_absoluto": settings.MAX_SITES_PER_USER,
        "valor_plano_pro": settings.PRO_PLAN_PRICE,
        "valor_site_extra": settings.EXTRA_SITE_PRICE,
        "busca_prospeccao": "ilimitada",
        "assinatura": {
            "status": assinatura["status"] if assinatura else None,
            "inicio": assinatura["inicio"] if assinatura else None,
            "valor": assinatura["valor"] if assinatura else None,
        } if assinatura else None
    }


def obter_planos_disponiveis() -> list:
    """Retorna a lista de planos disponiveis para exibir na pagina de precos."""
    return [
        {
            "id": "free",
            "nome": "Gratuito",
            "preco": 0,
            "periodo": "",
            "destaque": False,
            "recursos": [
                f"Ate {settings.FREE_SITES_LIMIT} sites gratuitos",
                "Templates profissionais",
                "Preview do site",
                "Busca de prospeccao ilimitada",
                "Suporte por email"
            ],
            "limitacoes": [
                "Sem dominio personalizado",
                "Marca d'agua SitesPro"
            ]
        },
        {
            "id": "pro",
            "nome": "Pro",
            "preco": settings.PRO_PLAN_PRICE,
            "periodo": "/mes",
            "destaque": True,
            "recursos": [
                f"Ate {settings.PRO_SITES_LIMIT} sites",
                "Templates profissionais",
                "Publicacao de sites",
                "Dominio personalizado",
                "Busca de prospeccao ilimitada",
                "Edicao avancada",
                "Sem marca d'agua",
                "Suporte prioritario"
            ],
            "limitacoes": []
        },
        {
            "id": "extra",
            "nome": "Site Extra",
            "preco": settings.EXTRA_SITE_PRICE,
            "periodo": "/site",
            "destaque": False,
            "recursos": [
                "1 site adicional alem do plano Pro",
                "Todas as funcionalidades Pro",
                f"Maximo de {settings.MAX_SITES_PER_USER} sites por conta"
            ],
            "limitacoes": [
                "Requer plano Pro ativo"
            ]
        }
    ]
