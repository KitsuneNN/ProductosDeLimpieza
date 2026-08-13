# -*- coding: utf-8 -*-
"""Endpoints de solicitudes: cliente y admin (B-T5)."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import DetalleSolicitud, Solicitud, Usuario
from app.schemas import (
    DetalleSolicitudPublic,
    PagoResponse,
    SolicitudAdminPublic,
    SolicitudCreate,
    SolicitudPublic,
    SolicitudesAdminResponse,
    SolicitudesResponse,
)
from app.services.requests import cancelar_solicitud, crear_solicitud
from app.ws.manager import manager

router_cliente = APIRouter(prefix="/solicitudes", tags=["solicitudes"])
router_admin = APIRouter(prefix="/admin/solicitudes", tags=["admin-solicitudes"])


def _a_publica(s: Solicitud) -> SolicitudPublic:
    return SolicitudPublic(
        id=s.id,
        usuario_id=s.usuario_id,
        estado=s.estado,
        total=s.total,
        creado_en=s.creado_en,
        pagada_en=s.pagada_en,
        items=[
            DetalleSolicitudPublic(
                producto_id=d.producto_id,
                nombre_producto=d.producto.nombre if d.producto else "(producto)",
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
            )
            for d in s.detalles
        ],
    )


async def _cargar_con_detalles(db: AsyncSession, solicitud_id: int) -> Solicitud | None:
    return (
        await db.execute(
            select(Solicitud)
            .where(Solicitud.id == solicitud_id)
            .options(selectinload(Solicitud.detalles).selectinload(DetalleSolicitud.producto))
        )
    ).scalar_one_or_none()


# ------------------------------------------------------------------ CLIENTE
@router_cliente.post("", response_model=SolicitudPublic, status_code=201)
async def crear(
    body: SolicitudCreate,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SolicitudPublic:
    solicitud = await crear_solicitud(db, usuario.id, body.items)
    # Aviso sonoro del admin: broadcast a todos los conectados con rol admin
    await manager.enviar_a_rol(
        "admin",
        "solicitud.creada",
        {
            "solicitud_id": solicitud.id,
            "usuario": {"id": usuario.id, "nombre": usuario.nombre},
            "total": solicitud.total,
            "creado_en": solicitud.creado_en.isoformat()
            if isinstance(solicitud.creado_en, datetime)
            else str(solicitud.creado_en),
            "resumen": [
                {
                    "producto_id": d.producto_id,
                    "nombre": d.producto.nombre if d.producto else "",
                    "cantidad": d.cantidad,
                }
                for d in solicitud.detalles
            ],
        },
    )
    return _a_publica(solicitud)


@router_cliente.get("/mias", response_model=SolicitudesResponse)
async def mis_solicitudes(
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SolicitudesResponse:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    condicion = Solicitud.usuario_id == usuario.id
    total = (
        await db.execute(select(func.count()).select_from(Solicitud).where(condicion))
    ).scalar_one()
    filas = (
        await db.execute(
            select(Solicitud)
            .where(condicion)
            .options(selectinload(Solicitud.detalles).selectinload(DetalleSolicitud.producto))
            .order_by(Solicitud.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()
    return SolicitudesResponse(
        items=[_a_publica(s) for s in filas],
        page=page,
        page_size=page_size,
        total=total,
    )


@router_cliente.get("/{solicitud_id}", response_model=SolicitudPublic)
async def detalle_propia(
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SolicitudPublic:
    solicitud = await _cargar_con_detalles(db, solicitud_id)
    if solicitud is None or solicitud.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitud inexistente")
    return _a_publica(solicitud)


@router_cliente.post("/{solicitud_id}/cancelar", response_model=SolicitudPublic)
async def cancelar_propia(
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SolicitudPublic:
    solicitud = await db.get(Solicitud, solicitud_id)
    if solicitud is None or solicitud.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitud inexistente")
    await cancelar_solicitud(db, solicitud, por="cliente")
    await manager.broadcast(
        "solicitud.cancelada",
        {"solicitud_id": solicitud.id, "usuario_id": solicitud.usuario_id, "por": "cliente"},
    )
    return _a_publica(await _cargar_con_detalles(db, solicitud_id))  # type: ignore[arg-type]


# -------------------------------------------------------------------- ADMIN
@router_admin.get("", response_model=SolicitudesAdminResponse)
async def listar_todas(
    estado: str | None = None,
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SolicitudesAdminResponse:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    condiciones = []
    if estado:
        condiciones.append(Solicitud.estado == estado)
    total = (
        await db.execute(
            select(func.count()).select_from(Solicitud).where(*condiciones)
        )
    ).scalar_one()
    filas = (
        await db.execute(
            select(Solicitud)
            .where(*condiciones)
            .options(
                selectinload(Solicitud.detalles).selectinload(DetalleSolicitud.producto),
                selectinload(Solicitud.usuario),
            )
            .order_by(Solicitud.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()
    return SolicitudesAdminResponse(
        items=[
            SolicitudAdminPublic(
                **_a_publica(s).model_dump(),
                usuario={
                    "id": s.usuario.id,
                    "nombre": s.usuario.nombre,
                    "telefono": s.usuario.telefono,
                    "email": s.usuario.email,
                    "rol": s.usuario.rol,
                    "creado_en": s.usuario.creado_en,
                },
            )
            for s in filas
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


@router_admin.get("/{solicitud_id}", response_model=SolicitudAdminPublic)
async def detalle_admin(
    solicitud_id: int,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SolicitudAdminPublic:
    solicitud = (
        await db.execute(
            select(Solicitud)
            .where(Solicitud.id == solicitud_id)
            .options(
                selectinload(Solicitud.detalles).selectinload(DetalleSolicitud.producto),
                selectinload(Solicitud.usuario),
            )
        )
    ).scalar_one_or_none()
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud inexistente")
    return SolicitudAdminPublic(
        **_a_publica(solicitud).model_dump(),
        usuario={
            "id": solicitud.usuario.id,
            "nombre": solicitud.usuario.nombre,
            "telefono": solicitud.usuario.telefono,
            "email": solicitud.usuario.email,
            "rol": solicitud.usuario.rol,
            "creado_en": solicitud.usuario.creado_en,
        },
    )


@router_admin.post("/{solicitud_id}/cancelar", response_model=SolicitudAdminPublic)
async def cancelar_admin(
    solicitud_id: int,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SolicitudAdminPublic:
    solicitud = await db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud inexistente")
    await cancelar_solicitud(db, solicitud, por="admin")
    await manager.broadcast(
        "solicitud.cancelada",
        {"solicitud_id": solicitud.id, "usuario_id": solicitud.usuario_id, "por": "admin"},
    )
    return await detalle_admin(solicitud_id, _, db)


# --------------------------------------------------------------- PAGO (B-T6)
@router_admin.post("/{solicitud_id}/pagar", response_model=PagoResponse)
async def pagar(
    solicitud_id: int,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PagoResponse:
    """Descuenta stock transaccionalmente (ver servicios/checkout.py)."""
    from app.services.checkout import pagar_solicitud

    return await pagar_solicitud(db, solicitud_id)
