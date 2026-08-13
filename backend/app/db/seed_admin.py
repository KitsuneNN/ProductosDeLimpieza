# -*- coding: utf-8 -*-
"""Crea el usuario administrador inicial (B-T2).

Uso:
    cd backend
    ADMIN_EMAIL=admin@limpieza.local ADMIN_PASSWORD=MiClaveSegura123 \
        .venv/bin/python -m app.db.seed_admin

Si ADMIN_PASSWORD no se define, se genera una contraseña aleatoria y se imprime
una única vez. Idempotente: si el admin existe, no lo duplica.
"""
import asyncio
import os
import secrets

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Usuario


async def crear_admin() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@limpieza.com").lower().strip()
    password = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(12)
    async with SessionLocal() as db:
        usuario = (
            await db.execute(select(Usuario).where(Usuario.email == email))
        ).scalar_one_or_none()
        if usuario is not None:
            if usuario.rol != "admin":
                usuario.rol = "admin"
                await db.commit()
            print(f"ℹ️  Admin ya existente: {email} (rol={usuario.rol})")
            return
        db.add(
            Usuario(
                nombre="Administrador",
                telefono="-",
                email=email,
                password_hash=hash_password(password),
                rol="admin",
            )
        )
        await db.commit()
        print("✅ Admin creado:")
        print(f"   email:    {email}")
        print(f"   password: {password}")
        print("   (guardá esta contraseña; no se vuelve a mostrar)")


if __name__ == "__main__":
    asyncio.run(crear_admin())
