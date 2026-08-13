# -*- coding: utf-8 -*-
"""Catálogo y categorías para CLIENTES (B-T4).

Aquí NUNCA se expone stock numérico: solo la etiqueta `disponibilidad`.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Categoria, Producto, Usuario
from app.schemas import (
    CatalogoResponse,
    CategoriasResponse,
    ProductoClientePublic,
)
from app.services.availability import etiqueta, obtener_umbral

router = APIRouter(tags=["catalogo"])


def _a_cliente(p: Producto, umbral: int) -> ProductoClientePublic:
    return ProductoClientePublic(
        id=p.id,
        categoria_id=p.categoria_id,
        nombre=p.nombre,
        descripcion=p.descripcion,
        precio=p.precio,
        imagen_url=p.imagen_url,
        disponibilidad=etiqueta(p.stock_actual, umbral),
    )


@router.get("/categorias", response_model=CategoriasResponse)
async def listar_categorias(
    _: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CategoriasResponse:
    filas = (
        await db.execute(select(Categoria).order_by(Categoria.orden.asc(), Categoria.id.asc()))
    ).scalars().all()
    return CategoriasResponse(items=filas)


@router.get("/catalogo", response_model=CatalogoResponse)
async def catalogo(
    categoria_id: int | None = None,
    busqueda: str | None = None,
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    _: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CatalogoResponse:
    """Catálogo paginado de productos ACTIVOS, con etiqueta de disponibilidad."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    condiciones = [Producto.estado == "activo"]
    if categoria_id is not None:
        condiciones.append(Producto.categoria_id == categoria_id)
    if busqueda and busqueda.strip():
        condiciones.append(Producto.nombre.ilike(f"%{busqueda.strip()}%"))

    total = (
        await db.execute(select(func.count()).select_from(Producto).where(*condiciones))
    ).scalar_one()
    filas = (
        await db.execute(
            select(Producto)
            .where(*condiciones)
            .order_by(Producto.nombre.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    umbral = await obtener_umbral(db)
    return CatalogoResponse(
        items=[_a_cliente(p, umbral) for p in filas],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/catalogo/{producto_id}", response_model=ProductoClientePublic)
async def detalle_catalogo(
    producto_id: int,
    _: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductoClientePublic:
    producto = await db.get(Producto, producto_id)
    if producto is None or producto.estado != "activo":
        raise HTTPException(status_code=404, detail="Producto no disponible")
    umbral = await obtener_umbral(db)
    return _a_cliente(producto, umbral)
