# -*- coding: utf-8 -*-
"""Checkout transaccional: pago de una solicitud (B-T6).

REGLAS:
- Solo solicitudes `pendiente` se pagan (409 si no).
- Se bloquean los productos con SELECT ... FOR UPDATE (concurrencia segura).
- Si falta stock de CUALQUIER ítem → StockInsuficienteError (HTTP 409 con
  lista de faltantes). NO se descuenta nada parcial.
- Al pagar: descuento real de stock + estado `pagada` + broadcast WS
  (`solicitud.pagada` y `stock.actualizado` con SOLO etiquetas).
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Producto, Solicitud
from app.schemas import FaltanteInfo, PagoResponse
from app.services.availability import etiqueta, obtener_umbral
from app.ws.manager import manager

if TYPE_CHECKING:
    pass


class StockInsuficienteError(Exception):
    """Stock insuficiente al pagar: 409 con lista de faltantes."""

    def __init__(self, faltantes: list[FaltanteInfo]) -> None:
        super().__init__("Stock insuficiente para completar la solicitud")
        self.faltantes = faltantes


async def pagar_solicitud(db: AsyncSession, solicitud_id: int) -> PagoResponse:
    solicitud = (
        await db.execute(
            select(Solicitud)
            .where(Solicitud.id == solicitud_id)
            .options(selectinload(Solicitud.detalles))
        )
    ).scalar_one_or_none()
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud inexistente")
    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La solicitud ya está en estado '{solicitud.estado}'",
        )

    detalles = sorted(solicitud.detalles, key=lambda d: d.id)
    ids = [d.producto_id for d in detalles]

    # Bloqueo de filas → dos pagos simultáneos no pueden sobre-vender.
    productos = (
        (
            await db.execute(
                select(Producto).where(Producto.id.in_(ids)).with_for_update()
            )
        )
        .scalars()
        .all()
    )
    mapa = {p.id: p for p in productos}

    faltantes: list[FaltanteInfo] = []
    for d in detalles:
        producto = mapa.get(d.producto_id)
        if producto is None or producto.stock_actual < d.cantidad:
            faltantes.append(
                FaltanteInfo(
                    producto_id=d.producto_id,
                    nombre=producto.nombre if producto else "(eliminado)",
                    solicitado=d.cantidad,
                    disponible=producto.stock_actual if producto else 0,
                )
            )
    if faltantes:
        raise StockInsuficienteError(faltantes)

    unidades_descontadas = 0
    for d in detalles:
        producto = mapa[d.producto_id]
        producto.stock_actual -= d.cantidad
        unidades_descontadas += d.cantidad

    solicitud.estado = "pagada"
    solicitud.pagada_en = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(solicitud)

    umbral = await obtener_umbral(db)
    # Broadcast: pago + nuevas etiquetas de los productos afectados (sin números)
    await manager.broadcast(
        "solicitud.pagada",
        {
            "solicitud_id": solicitud.id,
            "usuario_id": solicitud.usuario_id,
            "pagada_en": solicitud.pagada_en.isoformat(),
        },
    )
    await manager.enviar_a_rol(
        "cliente",
        "stock.actualizado",
        {
            "productos": [
                {
                    "producto_id": p.id,
                    "disponibilidad": etiqueta(p.stock_actual, umbral),
                }
                for p in productos
            ]
        },
    )
    return PagoResponse(
        solicitud_id=solicitud.id,
        estado="pagada",
        total=solicitud.total,
        pagada_en=solicitud.pagada_en,
        unidades_descontadas=unidades_descontadas,
    )
