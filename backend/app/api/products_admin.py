# -*- coding: utf-8 -*-
"""CRUD de productos — SOLO administradores (B-T3).

El stock numérico aparece únicamente aquí (vista admin). Los endpoints de
cliente usan el catálogo con etiquetas de disponibilidad.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin
from app.db.session import get_db
from app.models import Categoria, Producto, Usuario
from app.schemas import (
    ProductoAdminPublic,
    ProductoCreate,
    ProductoEstadoUpdate,
    ProductosAdminResponse,
    ProductoUpdate,
)
from app.services.images import images_service

router = APIRouter(prefix="/admin/productos", tags=["admin-productos"])

PAGE_SIZE_MAX = 100


@router.get("", response_model=ProductosAdminResponse)
async def listar_productos(
    categoria_id: int | None = None,
    busqueda: str | None = None,
    page: int = 1,
    page_size: int = 20,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ProductosAdminResponse:
    """Lista paginada de TODOS los productos (incluye pausados y stock)."""
    page = max(1, page)
    page_size = min(max(1, page_size), PAGE_SIZE_MAX)

    condiciones = []
    if categoria_id is not None:
        condiciones.append(Producto.categoria_id == categoria_id)
    if busqueda:
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
    return ProductosAdminResponse(
        items=filas, page=page, page_size=page_size, total=total
    )


@router.post("", response_model=ProductoAdminPublic, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    body: ProductoCreate,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Producto:
    categoria = await db.get(Categoria, body.categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría inexistente")
    producto = Producto(**body.model_dump())
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return producto


@router.get("/{producto_id}", response_model=ProductoAdminPublic)
async def detalle_producto(
    producto_id: int,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Producto:
    producto = await db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    return producto


@router.put("/{producto_id}", response_model=ProductoAdminPublic)
async def editar_producto(
    producto_id: int,
    body: ProductoUpdate,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Producto:
    producto = await db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    cambios = body.model_dump(exclude_unset=True)
    if "categoria_id" in cambios:
        if await db.get(Categoria, cambios["categoria_id"]) is None:
            raise HTTPException(status_code=404, detail="Categoría inexistente")
    for campo, valor in cambios.items():
        setattr(producto, campo, valor)
    await db.commit()
    await db.refresh(producto)
    return producto


@router.patch("/{producto_id}/estado", response_model=ProductoAdminPublic)
async def cambiar_estado(
    producto_id: int,
    body: ProductoEstadoUpdate,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Producto:
    """Activa o pausa un producto."""
    producto = await db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    producto.estado = body.estado
    await db.commit()
    await db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(
    producto_id: int,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Elimina un producto SIN historial de solicitudes (FK RESTRICT lo protege)."""
    producto = await db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    await db.delete(producto)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El producto tiene historial de solicitudes y no se puede eliminar. "
                "Podés pausarlo en su lugar."
            ),
        )


@router.post("/{producto_id}/imagen", response_model=ProductoAdminPublic)
async def subir_imagen(
    producto_id: int,
    archivo: UploadFile,
    _: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Producto:
    """Sube la foto del producto (Cloudinary o fallback local)."""
    producto = await db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    producto.imagen_url = await images_service.guardar(archivo)
    await db.commit()
    await db.refresh(producto)
    return producto
