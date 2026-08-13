# -*- coding: utf-8 -*-
"""Schemas de productos (ARQ-T2).

REGLAS DE ORO:
- El stock numérico SOLO aparece en `ProductoAdminPublic` y en los payloads
  de administración (create/update). NUNCA en respuestas al cliente.
- El cliente recibe `ProductoClientePublic` con la etiqueta `disponibilidad`.
- Montos: `Decimal` en el servidor; se serializan a número float en JSON.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from .common import DISPONIBILIDAD, ESTADO_PRODUCTO, SchemaBase


class _MontoJson(SchemaBase):
    """Serializa montos Decimal como número float en JSON (precisión interna intacta)."""

    @field_serializer("precio", "total", "precio_unitario", when_used="json", check_fields=False)
    def _monto_a_float(self, valor: Decimal, _info) -> float:
        return float(valor)


class ProductoAdminPublic(_MontoJson):
    """Vista de administración — incluye stock numérico (solo admin)."""

    id: int
    categoria_id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    stock_actual: int
    imagen_url: str | None
    estado: ESTADO_PRODUCTO
    creado_en: datetime
    actualizado_en: datetime


class ProductoCreate(_MontoJson):
    categoria_id: int
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = None
    precio: Decimal = Field(ge=0)
    stock_actual: int = Field(default=0, ge=0)
    imagen_url: str | None = None
    estado: ESTADO_PRODUCTO = "activo"


class ProductoUpdate(_MontoJson):
    categoria_id: int | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    descripcion: str | None = None
    precio: Decimal | None = Field(default=None, ge=0)
    stock_actual: int | None = Field(default=None, ge=0)
    imagen_url: str | None = None
    estado: ESTADO_PRODUCTO | None = None


class ProductoEstadoUpdate(SchemaBase):
    estado: ESTADO_PRODUCTO


class ProductoClientePublic(_MontoJson):
    """Vista de cliente — SIN stock numérico, solo etiqueta de disponibilidad."""

    id: int
    categoria_id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    imagen_url: str | None
    disponibilidad: DISPONIBILIDAD


class ProductosAdminResponse(SchemaBase):
    """Listado paginado de productos (vista admin)."""

    items: list[ProductoAdminPublic]
    page: int
    page_size: int
    total: int
