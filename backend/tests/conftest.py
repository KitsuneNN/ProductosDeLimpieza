# -*- coding: utf-8 -*-
"""Fixtures compartidas de tests (QA).

Base de datos: SQLite en memoria por sesión de tests con la app sobre ASGI
directo (ASGITransport) — sin red. Las tablas se crean desde Base.metadata y
se siembran datos de prueba (config, categorías, admin, cliente, productos).
"""
import os
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Base,
    Categoria,
    Configuracion,
    Producto,
    Usuario,
)

URL_TEST = "sqlite+aiosqlite:///./test.db"


@pytest.fixture
async def client():
    engine = create_async_engine(URL_TEST)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    SessionTest = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionTest() as db:
        db.add_all(
            [
                Categoria(nombre="Detergentes", orden=1),
                Categoria(nombre="Lavandinas", orden=2),
                Configuracion(clave="umbral_pocas_unidades", valor="5"),
                Usuario(
                    nombre="Administrador",
                    telefono="-",
                    email="admin@limpieza.com",
                    password_hash="hash_admin",
                    rol="admin",
                ),
                Usuario(
                    nombre="Cliente Uno",
                    telefono="2615551234",
                    email="cliente@example.com",
                    password_hash="hash_cliente",
                    rol="cliente",
                ),
                Producto(
                    categoria_id=1,
                    nombre="Lavandina 1L",
                    descripcion="Lavandina concentrada",
                    precio=Decimal("1250.50"),
                    stock_actual=10,
                    estado="activo",
                ),
                Producto(
                    categoria_id=2,
                    nombre="Detergente Limón",
                    descripcion=None,
                    precio=Decimal("800.00"),
                    stock_actual=3,
                    estado="activo",
                ),
                Producto(
                    categoria_id=1,
                    nombre="Producto Pausado",
                    descripcion=None,
                    precio=Decimal("100.00"),
                    stock_actual=50,
                    estado="pausado",
                ),
            ]
        )
        await db.commit()

    async def override_get_db():
        async with SessionTest() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()
