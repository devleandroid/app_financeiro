"""Router de autenticacao - registro, login, perfil."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.infrastructure.auth.jwt_auth import (
    registrar_usuario,
    login_usuario,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    nome: str
    telefone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(req: RegisterRequest):
    """
    Cadastrar um novo usuario.

    - **email**: Email do usuario (unico)
    - **password**: Senha (minimo 6 caracteres)
    - **nome**: Nome completo
    - **telefone**: Telefone (opcional)

    Retorna o token JWT e dados do usuario.
    """
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="A senha deve ter no minimo 6 caracteres")

    if not req.nome.strip():
        raise HTTPException(status_code=400, detail="O nome e obrigatorio")

    try:
        result = registrar_usuario(req.email, req.password, req.nome, req.telefone)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(req: LoginRequest):
    """
    Fazer login e receber token JWT.

    - **email**: Email cadastrado
    - **password**: Senha

    Retorna o token JWT e dados do usuario.
    """
    try:
        result = login_usuario(req.email, req.password)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """
    Retorna os dados do usuario logado.

    Requer token JWT no header Authorization: Bearer <token>
    """
    return {"success": True, "user": user}
