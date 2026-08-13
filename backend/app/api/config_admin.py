# -*- coding: utf-8 -*-
"""Configuración del negocio — solo admin (B-T6).

Clave principal del MVP: `umbral_pocas_unidades` (requisito 20.1 del proyecto).
Al cambiarlo se re-etiquetan en vivo todos los productos (broadcast WS con
SOLO etiquetas, nunca números).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin
from app.db.session import get_db
from app.models import Configuracion, Producto, Usuario
from app.schemas import ConfiguracionesResponse, ConfiguracionUpdate, UmbralResponse
from app.services.availability import etiqueta, obtener_umbral
from app.ws.manager import manager

router = APIRouter(prefix="/admin/config", tags=["admin-config"])

CLAVE_UMBRAL = "umbral_pocas_unidades"


@router.get("", response_model=ConfiguracionesResponse)
async def listar_config(
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ConfiguracionesResponse:
    filas = (await db.execute(select(Configuracion))).scalars().all()
    return ConfiguracionesResponse(items=filas)


@router.get("/umbral-pocas-unidades", response_model=UmbralResponse)
async def leer_umbral(
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UmbralResponse:
    return UmbralResponse(umbral_pocas_unidades=await obtener_umbral(db))


@router.put("/umbral-pocas-unidades", response_model=UmbralResponse)
async def cambiar_umbral(
    body: ConfiguracionUpdate,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UmbralResponse:
    try:
        valor = int(body.valor)
    except ValueError:
        raise HTTPException(status_code=400, detail="El umbral debe ser un número entero")
    if valor < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El umbral debe ser al menos 1",
        )
    fila = await db.get(Configuracion, CLAVE_UMBRAL)
    if fila is None:
        db.add(Configuracion(clave=CLAVE_UMBRAL, valor=str(valor)))
    else:
        fila.valor = str(valor)
    await db.commit()

    # Re-etiquetar en vivo: broadcast de etiquetas de TODOS los activos (sin números)
    productos = (
        (await db.execute(select(Producto).where(Producto.estado == "activo")))
        .scalars()
        .all()
    )
    await manager.enviar_a_rol(
        "cliente",
        "stock.actualizado",
        {
            "productos": [
                {"producto_id": p.id, "disponibilidad": etiqueta(p.stock_actual, valor)}
                for p in productos
            ]
        },
    )
    return UmbralResponse(umbral_pocas_unidades=valor)
