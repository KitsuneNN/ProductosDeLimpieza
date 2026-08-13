# -*- coding: utf-8 -*-
"""Etiquetas de disponibilidad para el cliente (B-T4).

REGLA DE ORO: el cliente NUNCA ve el stock numérico — solo etiquetas:
- `disponible` → stock > umbral
- `pocas`     → 0 < stock ≤ umbral
- `sin_stock` → stock == 0
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Configuracion
from app.schemas import DISPONIBILIDAD

UMBRAL_POR_DEFECTO = 5
CLAVE_UMBRAL = "umbral_pocas_unidades"


async def obtener_umbral(db: AsyncSession) -> int:
    """Lee el umbral configurado (default 5). Clampea a >= 1."""
    fila = await db.get(Configuracion, CLAVE_UMBRAL)
    if fila is None:
        return UMBRAL_POR_DEFECTO
    try:
        return max(1, int(fila.valor))
    except (TypeError, ValueError):
        return UMBRAL_POR_DEFECTO


def etiqueta(stock: int, umbral: int) -> DISPONIBILIDAD:
    """Calcula la etiqueta de disponibilidad a partir del stock y el umbral."""
    if stock <= 0:
        return "sin_stock"
    if stock <= umbral:
        return "pocas"
    return "disponible"
