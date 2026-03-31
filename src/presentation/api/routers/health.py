"""Endpoint de health check e keep-alive"""
from fastapi import APIRouter
from datetime import datetime
import asyncio

router = APIRouter(tags=["health"])

# Contador de requisições para debug
request_counter = 0

@router.get("/health")
async def health_check():
    """Endpoint básico de health check"""
    global request_counter
    request_counter += 1
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "investsmart-backend",
        "requests": request_counter
    }

@router.get("/ping")
async def ping():
    """Endpoint simples para teste de conectividade"""
    return {
        "pong": True,
        "time": datetime.now().isoformat()
    }

@router.get("/keep-alive")
async def keep_alive():
    """Endpoint para manter o serviço ativo (evita dormir no free tier)"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "message": "Service is running"
    }