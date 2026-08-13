# -*- coding: utf-8 -*-
"""Tests del checkout transaccional (B-T6)."""
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Producto, Solicitud
from app.services.checkout import StockInsuficienteError, pagar_solicitud
from app.services.requests import crear_solicitud
from app.schemas import ItemSolicitudCreate

URL_TEST = "sqlite+aiosqlite:///./test.db"


async def _sesion():
    engine = create_async_engine(URL_TEST)
    S = async_sessionmaker(engine, expire_on_commit=False)
    return engine, S()


@pytest.mark.asyncio
async def test_pagar_descuenta_stock_y_marca_pagada(client):
    engine, db = await _sesion()
    try:
        solicitud = await crear_solicitud(
            db, 2, [ItemSolicitudCreate(producto_id=1, cantidad=2)]
        )
        resultado = await pagar_solicitud(db, solicitud.id)
        assert resultado.estado == "pagada"
        assert resultado.unidades_descontadas == 2
        producto = await db.get(Producto, 1)
        assert producto.stock_actual == 8  # 10 - 2
        sol = await db.get(Solicitud, solicitud.id)
        assert sol.estado == "pagada"
        assert sol.pagada_en is not None
    finally:
        await db.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pagar_con_stock_insuficiente_409_sin_descuento_parcial(client):
    engine, db = await _sesion()
    try:
        solicitud = await crear_solicitud(
            db, 2, [ItemSolicitudCreate(producto_id=2, cantidad=999)]
        )
        with pytest.raises(StockInsuficienteError) as exc:
            await pagar_solicitud(db, solicitud.id)
        assert len(exc.value.faltantes) == 1
        f = exc.value.faltantes[0]
        assert f.producto_id == 2 and f.disponible == 3
        producto = await db.get(Producto, 2)
        assert producto.stock_actual == 3  # nada se descontó
    finally:
        await db.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pagar_solicitud_ya_pagada_409(client):
    engine, db = await _sesion()
    try:
        solicitud = await crear_solicitud(
            db, 2, [ItemSolicitudCreate(producto_id=1, cantidad=1)]
        )
        await pagar_solicitud(db, solicitud.id)
        with pytest.raises(HTTPException) as exc:
            await pagar_solicitud(db, solicitud.id)
        assert exc.value.status_code == 409
    finally:
        await db.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pagar_solicitud_cancelada_409(client):
    engine, db = await _sesion()
    try:
        solicitud = await crear_solicitud(
            db, 2, [ItemSolicitudCreate(producto_id=1, cantidad=1)]
        )
        from app.services.requests import cancelar_solicitud

        await cancelar_solicitud(db, solicitud, por="cliente")
        with pytest.raises(HTTPException) as exc:
            await pagar_solicitud(db, solicitud.id)
        assert exc.value.status_code == 409
    finally:
        await db.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pagar_inexistente_404(client):
    engine, db = await _sesion()
    try:
        with pytest.raises(HTTPException) as exc:
            await pagar_solicitud(db, 999999)
        assert exc.value.status_code == 404
    finally:
        await db.close()
        await engine.dispose()
