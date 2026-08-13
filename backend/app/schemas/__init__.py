# -*- coding: utf-8 -*-
"""Export central de schemas (ARQ-T2)."""
from .auth import LoginRequest, RegistroRequest, TokenResponse, UsuarioPublic
from .catalogo import CatalogoResponse, CategoriasResponse
from .categoria import CategoriaCreate, CategoriaPublic, CategoriaUpdate
from .common import (
    DISPONIBILIDAD,
    ESTADO_PRODUCTO,
    ESTADO_SOLICITUD,
    ROL_USUARIO,
    SchemaBase,
)
from .configuracion import ConfiguracionPublic, ConfiguracionUpdate, UmbralResponse
from .producto import (
    ProductoAdminPublic,
    ProductoClientePublic,
    ProductoCreate,
    ProductoEstadoUpdate,
    ProductoUpdate,
)
from .solicitud import (
    DetalleSolicitudPublic,
    FaltanteInfo,
    FaltantesResponse,
    ItemSolicitudCreate,
    PagoResponse,
    SolicitudAdminPublic,
    SolicitudCreate,
    SolicitudPublic,
    SolicitudesAdminResponse,
    SolicitudesResponse,
)

__all__ = [
    "DISPONIBILIDAD",
    "ESTADO_PRODUCTO",
    "ESTADO_SOLICITUD",
    "ROL_USUARIO",
    "SchemaBase",
    "LoginRequest",
    "RegistroRequest",
    "TokenResponse",
    "UsuarioPublic",
    "CatalogoResponse",
    "CategoriasResponse",
    "CategoriaCreate",
    "CategoriaPublic",
    "CategoriaUpdate",
    "ConfiguracionPublic",
    "ConfiguracionUpdate",
    "UmbralResponse",
    "ProductoAdminPublic",
    "ProductoClientePublic",
    "ProductoCreate",
    "ProductoEstadoUpdate",
    "ProductoUpdate",
    "DetalleSolicitudPublic",
    "FaltanteInfo",
    "FaltantesResponse",
    "ItemSolicitudCreate",
    "PagoResponse",
    "SolicitudAdminPublic",
    "SolicitudCreate",
    "SolicitudPublic",
    "SolicitudesAdminResponse",
    "SolicitudesResponse",
]
