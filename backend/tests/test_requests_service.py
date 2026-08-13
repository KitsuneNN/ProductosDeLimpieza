# -*- coding: utf-8 -*-
"""Tests del servicio de solicitudes (B-T5)."""
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.schemas import ItemSolicitudCreate
from app.services.requests import cancelar_solicitud, crear_solicitud

URL_TEST = "sqlite+aiosqlite:///./test.db"


@pytest.mark.asyncio
async def test_crear_solicitud_total_server_side(client):
    engine = create_async_engine(URL_TEST)
    S = async_sessionmaker(engine, expire_on_commit=False)
    async with S() as db:
        solicitud = await crear_solicitud(
            db,
            2,
            [
                ItemSolicitudCreate(producto_id=1, cantidad=2),  # 1250.50 * 2
                ItemSolicitudCreate(producto_id=2, cantidad=1),  # 800.00
            ],
        )
        assert solicitud.estado == "pendiente"
        assert solicitud.total == Decimal("3301.00")
        assert len(solicitud.detalles) == 2
        # snapshot de precio guardado
        assert solicitud.detalles[0].precio_unitario == Decimal("1250.50")
    await engine.dispose()


@pytest.mark.asyncio
async def test_crear_con_producto_inexistente_404(client):
    engine = create_async_engine(URL_TEST)
    S = async_sessionmaker(engine, expire_on_commit=False)
    async with S() as db:
        with pytest.raises(HTTPException) as exc:
            await crear_solicitud(db, 2, [ItemSolicitudCreate(producto_id=999, cantidad=1)])
        assert exc.value.status_code == 404
    await engine.dispose()


@pytest.mark.asyncio
async def test_crear_con_producto_pausado_400(client):
    engine = create_async_engine(URL_TEST)
    S = async_sessionmaker(engine, expire_on_commit=False)
    async with S() as db:
        with pytest.raises(HTTPException) as exc:
            await crear_solicitud(db, 2, [ItemSolicitudCreate(producto_id=3, cantidad=1)])
        assert exc.value.status_code == 400
    await engine.dispose()


@pytest.mark.asyncio
async def test_cancelar_maquina_de_estados(client):
    engine = create_async_engine(URL_TEST)
    S = async_sessionmaker(engine, expire_on_commit=False)
    async with S() as db:
        solicitud = await crear_solicitud(
            db, 2, [ItemSolicitudCreate(producto_id=1, cantidad=1)]
        )
        await cancelar_solicitud(db, solicitud, por="cliente")
        assert solicitud.estado == "cancelada"
        with pytest.raises(HTTPException) as exc:
            await cancelar_solicitud(db, solicitud, por="cliente")
        assert exc.value.status_code == 409  # ya no está pendiente
    await engine.dispose()
