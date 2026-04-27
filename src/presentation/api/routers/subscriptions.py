"""Router de assinaturas e planos."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.auth.jwt_auth import get_current_user
from src.infrastructure.database import site_repository_sqlite as repo
from src.application.services.plan_service import obter_info_plano, obter_planos_disponiveis
from src.infrastructure.config.settings import settings

router = APIRouter(prefix="/subscriptions", tags=["Assinaturas"])


class CheckoutRequest(BaseModel):
    plano: str = "pro"
    gateway: Optional[str] = None


class ExtraSitePaymentRequest(BaseModel):
    site_id: int


@router.get("/plans")
async def listar_planos():
    """Retorna os planos disponiveis com precos e recursos."""
    planos = obter_planos_disponiveis()
    return {"success": True, "planos": planos}


@router.get("/status")
async def status_assinatura(user: dict = Depends(get_current_user)):
    """Retorna o status do plano e assinatura do usuario."""
    info = obter_info_plano(user["id"])
    return {"success": True, **info}


@router.post("/checkout")
async def iniciar_checkout(req: CheckoutRequest, user: dict = Depends(get_current_user)):
    """
    Inicia o processo de assinatura do plano Pro.

    Em producao, isso criaria uma sessao de pagamento no Mercado Pago ou Stripe.
    No MVP, ativa o plano diretamente para demonstracao.
    """
    if user["plano"] == "pro":
        raise HTTPException(status_code=400, detail="Voce ja possui o plano Pro ativo")

    if req.plano != "pro":
        raise HTTPException(status_code=400, detail="Plano invalido")

    # TODO: Em producao, integrar com Mercado Pago / Stripe
    # Por enquanto, simulamos a ativacao do plano

    assinatura = repo.criar_assinatura(
        user_id=user["id"],
        plano="pro",
        valor=settings.PRO_PLAN_PRICE,
        payment_gateway=req.gateway or settings.PAYMENT_GATEWAY
    )

    repo.registrar_pagamento(
        user_id=user["id"],
        tipo="assinatura",
        valor=settings.PRO_PLAN_PRICE,
        descricao=f"Assinatura Plano Pro - R${settings.PRO_PLAN_PRICE:.2f}/mes",
        status="completed",
        gateway=req.gateway or settings.PAYMENT_GATEWAY
    )

    return {
        "success": True,
        "message": f"Plano Pro ativado com sucesso! R${settings.PRO_PLAN_PRICE:.2f}/mes",
        "assinatura": assinatura,
        "plano": "pro"
    }


@router.post("/cancel")
async def cancelar_assinatura_endpoint(user: dict = Depends(get_current_user)):
    """Cancela a assinatura do plano Pro."""
    if user["plano"] == "free":
        raise HTTPException(status_code=400, detail="Voce nao possui assinatura ativa")

    repo.cancelar_assinatura(user["id"])

    return {
        "success": True,
        "message": "Assinatura cancelada. Voce ainda pode usar os sites criados, mas nao pode publicar novos."
    }


@router.post("/pay-extra-site")
async def pagar_site_extra(req: ExtraSitePaymentRequest,
                           user: dict = Depends(get_current_user)):
    """
    Realiza o pagamento para um site extra (alem do limite do plano Pro).
    Custo: R$399,90 por site adicional.
    """
    if user["plano"] != "pro":
        raise HTTPException(
            status_code=403,
            detail="Voce precisa ter o plano Pro ativo para adquirir sites extras"
        )

    sites_count = repo.contar_sites_usuario(user["id"])
    if sites_count >= settings.MAX_SITES_PER_USER:
        raise HTTPException(
            status_code=403,
            detail=f"Limite maximo de {settings.MAX_SITES_PER_USER} sites atingido"
        )

    # TODO: Integrar com gateway de pagamento real
    repo.registrar_pagamento(
        user_id=user["id"],
        tipo="site_extra",
        valor=settings.EXTRA_SITE_PRICE,
        descricao=f"Site extra - Site ID: {req.site_id}",
        status="completed",
        gateway=settings.PAYMENT_GATEWAY
    )

    return {
        "success": True,
        "message": f"Pagamento de R${settings.EXTRA_SITE_PRICE:.2f} processado. Site extra liberado!",
        "valor": settings.EXTRA_SITE_PRICE
    }


@router.get("/payments")
async def listar_pagamentos(user: dict = Depends(get_current_user)):
    """Lista o historico de pagamentos do usuario."""
    pagamentos = repo.listar_pagamentos_usuario(user["id"])
    return {"success": True, "pagamentos": pagamentos}
