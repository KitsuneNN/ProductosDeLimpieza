# -*- coding: utf-8 -*-
"""Schemas de solicitudes (ARQ-T2)."""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from .auth import UsuarioPublic
from .common import ESTADO_SOLICITUD, SchemaBase
from .producto import _MontoJson


class ItemSolicitudCreate(SchemaBase):
    producto_id: int
    cantidad: int = Field(ge=1, le=999)


class SolicitudCreate(SchemaBase):
    items: list[ItemSolicitudCreate] = Field(min_length=1, max_length=50)


class DetalleSolicitudPublic(_MontoJson):
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal


class SolicitudPublic(_MontoJson):
    id: int
    usuario_id: int
    estado: ESTADO_SOLICITUD
    total: Decimal
    creado_en: datetime
    pagada_en: datetime | None
    items: list[DetalleSolicitudPublic]


class SolicitudAdminPublic(SolicitudPublic):
    """Vista de administración — agrega los datos del usuario."""

    usuario: UsuarioPublic


class SolicitudesResponse(SchemaBase):
    items: list[SolicitudPublic]
    page: int
    page_size: int
    total: int


class SolicitudesAdminResponse(SchemaBase):
    items: list[SolicitudAdminPublic]
    page: int
    page_size: int
    total: int


class PagoResponse(_MontoJson):
    """Resultado de POST /api/admin/solicitudes/{id}/pagar."""

    solicitud_id: int
    estado: Literal["pagada"]
    total: Decimal
    pagada_en: datetime
    unidades_descontadas: int


class FaltanteInfo(SchemaBase):
    """Producto con stock insuficiente al intentar pagar (HTTP 409)."""

    producto_id: int
    nombre: str
    solicitado: int
    disponible: int


class FaltantesResponse(SchemaBase):
    """Cuerpo del error 409: detalle + faltantes (no se descuenta nada parcial)."""

    detail: str
    faltantes: list[FaltanteInfo]
