"""Autenticacao JWT para a plataforma de sites."""
import hashlib
import hmac
import json
import base64
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.infrastructure.config.settings import settings
from src.infrastructure.database import site_repository_sqlite as repo

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def _hash_password(password: str) -> str:
    """Gera hash da senha usando SHA-256 com salt."""
    salt = settings.JWT_SECRET[:16]
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def _verificar_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return _hash_password(password) == password_hash


def _criar_jwt(payload: dict) -> str:
    """Cria um JWT manualmente (sem dependencia externa)."""
    header = {"alg": "HS256", "typ": "JWT"}

    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).rstrip(b"=").decode()

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()

    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        settings.JWT_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

    return f"{message}.{sig_b64}"


def _decodificar_jwt(token: str) -> Optional[dict]:
    """Decodifica e valida um JWT."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        message = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            settings.JWT_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b"=").decode()

        if not hmac.compare_digest(sig_b64, expected_b64):
            return None

        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None


def gerar_token(user_id: int, email: str) -> str:
    """Gera um token JWT para o usuario."""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": time.time() + (settings.JWT_EXPIRATION_HOURS * 3600),
        "iat": time.time()
    }
    return _criar_jwt(payload)


def registrar_usuario(email: str, password: str, nome: str, telefone: str = None) -> dict:
    """Registra um novo usuario."""
    password_hash = _hash_password(password)
    user = repo.criar_usuario(email, password_hash, nome, telefone)
    token = gerar_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "nome": user["nome"],
            "plano": user["plano"],
            "sites_criados": user["sites_criados"]
        }
    }


def login_usuario(email: str, password: str) -> dict:
    """Autentica um usuario e retorna token."""
    user = repo.buscar_usuario_por_email(email)
    if not user or not _verificar_password(password, user["password_hash"]):
        raise ValueError("Email ou senha invalidos")

    if not user.get("ativo", True):
        raise ValueError("Conta desativada")

    token = gerar_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "nome": user["nome"],
            "plano": user["plano"],
            "sites_criados": user["sites_criados"]
        }
    }


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None
) -> dict:
    """Dependency do FastAPI para obter o usuario logado."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao nao fornecido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = _decodificar_jwt(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = repo.buscar_usuario_por_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado"
        )

    return {
        "id": user["id"],
        "email": user["email"],
        "nome": user["nome"],
        "plano": user["plano"],
        "sites_criados": user["sites_criados"]
    }


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Dependency opcional - retorna None se nao autenticado."""
    if not credentials:
        return None

    payload = _decodificar_jwt(credentials.credentials)
    if not payload:
        return None

    user = repo.buscar_usuario_por_id(payload["sub"])
    if not user:
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "nome": user["nome"],
        "plano": user["plano"],
        "sites_criados": user["sites_criados"]
    }
