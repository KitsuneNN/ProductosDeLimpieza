# -*- coding: utf-8 -*-
"""Dependencias de autenticación y autorización (B-T2)."""
import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Devuelve el usuario autenticado del token Bearer (401 si no hay/inválido)."""
    if credenciales is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado"
        )
    try:
        payload = decode_access_token(credenciales.credentials)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión expirada"
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token inválido")
    try:
        usuario_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario inexistente")
    return usuario


async def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Exige rol admin (403 si no)."""
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol de administrador",
        )
    return usuario
