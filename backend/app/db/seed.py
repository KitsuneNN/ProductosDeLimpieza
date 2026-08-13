# -*- coding: utf-8 -*-
"""Seed idempotente: categorías base y configuración por defecto (ARQ-T1).

Se puede ejecutar cuantas veces sea necesario sin duplicar datos
(ON CONFLICT DO NOTHING).
"""
from sqlalchemy.dialects.postgresql import insert
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
    """Inserta categorías y configuración por defecto (idempotente)."""
    from app.models import Categoria, Configuracion

    for nombre in CATEGORIAS_BASE:
        session.execute(
            insert(Categoria)
            .values(nombre=nombre, orden=0)
            .on_conflict_do_nothing(index_elements=["nombre"])
        )
    for clave, valor in CONFIGURACION_DEFAULT.items():
        session.execute(
            insert(Configuracion)
            .values(clave=clave, valor=valor)
            .on_conflict_do_nothing(index_elements=["clave"])
        )
    session.commit()
