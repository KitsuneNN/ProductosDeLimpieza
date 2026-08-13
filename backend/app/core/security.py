# -*- coding: utf-8 -*-
"""Seguridad: hash de contraseñas (bcrypt) y tokens JWT (B-T2)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(contrasena: str) -> str:
    """Hash bcrypt de una contraseña (nunca texto plano en BD)."""
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(contrasena: str, hash_guardado: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(usuario_id: int, rol: str, minutos: int | None = None) -> str:
    """Genera un JWT firmado con sub=id, rol y expiración."""
    ahora = datetime.now(timezone.utc)
    expira = ahora + timedelta(minutes=minutos or settings.jwt_expires_minutes)
    payload = {"sub": str(usuario_id), "rol": rol, "iat": ahora, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifica y valida un JWT (firma + expiración). Lanza jwt.*Error si es inválido."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
