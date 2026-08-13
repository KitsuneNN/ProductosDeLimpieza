# -*- coding: utf-8 -*-
"""Endpoints de autenticación (B-T2)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import Usuario
from app.schemas import LoginRequest, RegistroRequest, TokenResponse, UsuarioPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registro",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registro(body: RegistroRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Registra un cliente y devuelve su token."""
    email = body.email.lower().strip()
    existe = (
        await db.execute(select(Usuario.id).where(Usuario.email == email))
    ).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese email",
        )
    usuario = Usuario(
        nombre=body.nombre.strip(),
        telefono=body.telefono.strip(),
        email=email,
        password_hash=hash_password(body.password),
        rol="cliente",
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    token = create_access_token(usuario.id, usuario.rol)
    return TokenResponse(access_token=token, token_type="bearer", usuario=usuario)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Inicia sesión (cliente o admin) y devuelve su token."""
    email = body.email.lower().strip()
    usuario = (
        await db.execute(select(Usuario).where(Usuario.email == email))
    ).scalar_one_or_none()
    if usuario is None or not verify_password(body.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    token = create_access_token(usuario.id, usuario.rol)
    return TokenResponse(access_token=token, token_type="bearer", usuario=usuario)


@router.get("/me", response_model=UsuarioPublic)
async def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Datos del usuario autenticado."""
    return usuario
