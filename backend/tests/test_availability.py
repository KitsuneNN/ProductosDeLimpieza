# -*- coding: utf-8 -*-
"""Tests de etiquetas de disponibilidad (B-T4)."""
import pytest

from app.services.availability import etiqueta, obtener_umbral


def test_etiqueta_fronteras():
    assert etiqueta(0, 5) == "sin_stock"
    assert etiqueta(1, 5) == "pocas"
    assert etiqueta(5, 5) == "pocas"  # frontera: stock == umbral → pocas
    assert etiqueta(6, 5) == "disponible"


def test_etiqueta_umbral_uno():
    assert etiqueta(1, 1) == "pocas"
    assert etiqueta(2, 1) == "disponible"


@pytest.mark.asyncio
async def test_obtener_umbral_desde_bd(client):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    S = async_sessionmaker(engine)
    async with S() as db:
        assert await obtener_umbral(db) == 5
    await engine.dispose()


@pytest.mark.asyncio
async def test_obtener_umbral_valor_invalido_clampea(client):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.models import Configuracion

    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    S = async_sessionmaker(engine)
    async with S() as db:
        fila = await db.get(Configuracion, "umbral_pocas_unidades")
        fila.valor = "basura"
        await db.commit()
        assert await obtener_umbral(db) == 5  # fallback seguro
    await engine.dispose()
