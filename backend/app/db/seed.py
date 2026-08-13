# -*- coding: utf-8 -*-
"""Seed idempotente: categorías base y configuración por defecto (ARQ-T1).

Dialect-agnóstico (funciona en PostgreSQL y SQLite): verifica existencia
antes de insertar, por lo que puede ejecutarse N veces sin duplicar datos.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

CATEGORIAS_BASE = [
    "Detergentes",
    "Lavandinas",
    "Desinfectantes",
    "Esponjas y trapos",
    "Aromatizantes",
    "Otros",
]

CONFIGURACION_DEFAULT = {
    "umbral_pocas_unidades": "5",
}


def seed(session: Session) -> None:
    """Inserta categorías (con orden) y configuración por defecto (idempotente)."""
    from app.models import Categoria, Configuracion

    for posicion, nombre in enumerate(CATEGORIAS_BASE, start=1):
        existe = session.execute(
            select(Categoria.id).where(Categoria.nombre == nombre)
        ).first()
        if not existe:
            session.add(Categoria(nombre=nombre, orden=posicion))

    for clave, valor in CONFIGURACION_DEFAULT.items():
        if session.get(Configuracion, clave) is None:
            session.add(Configuracion(clave=clave, valor=valor))

    session.commit()
