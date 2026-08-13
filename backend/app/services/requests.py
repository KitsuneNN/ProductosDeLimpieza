# -*- coding: utf-8 -*-
"""Servicio de solicitudes (B-T5).

- crear_solicitud: valida productos activos, congela precios unitarios
  (snapshot) y calcula el total SERVER-SIDE.
- cancelar_solicitud: respeta la máquina de estados (solo pendiente).
"""
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DetalleSolicitud, Producto, Solicitud
from app.schemas import ItemSolicitudCreate


async def crear_solicitud(
    db: AsyncSession, usuario_id: int, items: list[ItemSolicitudCreate]
) -> Solicitud:
    """Crea una solicitud `pendiente` con sus detalles y total calculado."""
    ids = [item.producto_id for item in items]
    productos = (
        (
            await db.execute(
                select(Producto).where(Producto.id.in_(ids))
            )
        )
        .scalars()
        .all()
    )
    mapa = {p.id: p for p in productos}
    faltantes_ids = [pid for pid in ids if pid not in mapa]
    if faltantes_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos inexistentes: {faltantes_ids}",
        )
    pausados = [p.id for p in productos if p.estado != "activo"]
    if pausados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Productos no disponibles: {pausados}",
        )

    solicitud = Solicitud(usuario_id=usuario_id, estado="pendiente", total=Decimal("0"))
    db.add(solicitud)
    await db.flush()  # para obtener solicitud.id

    total = Decimal("0")
    for item in items:
        producto = mapa[item.producto_id]
        total += producto.precio * item.cantidad
        db.add(
            DetalleSolicitud(
                solicitud_id=solicitud.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,  # snapshot del precio
            )
        )
    solicitud.total = total
    await db.commit()
    # recargar con detalles + producto para construir respuestas
    solicitud = (
        await db.execute(
            select(Solicitud)
            .where(Solicitud.id == solicitud.id)
            .options(selectinload(Solicitud.detalles).selectinload(DetalleSolicitud.producto))
        )
    ).scalar_one()
    return solicitud


async def cancelar_solicitud(
    db: AsyncSession, solicitud: Solicitud, por: str
) -> Solicitud:
    """Cancela una solicitud pendiente. `por` ∈ {cliente, admin}."""
    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La solicitud ya está en estado '{solicitud.estado}'",
        )
    solicitud.estado = "cancelada"
    await db.commit()
    await db.refresh(solicitud)
    return solicitud
