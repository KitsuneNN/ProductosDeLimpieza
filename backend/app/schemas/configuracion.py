# -*- coding: utf-8 -*-
"""Schemas de configuración (ARQ-T2)."""
from pydantic import Field

from .common import SchemaBase


class ConfiguracionPublic(SchemaBase):
    clave: str
    valor: str


class ConfiguracionUpdate(SchemaBase):
    valor: str = Field(max_length=255)


class UmbralResponse(SchemaBase):
    """Respuesta cómoda de GET /api/admin/config/umbral-pocas-unidades."""

    umbral_pocas_unidades: int = Field(ge=1)


class ConfiguracionesResponse(SchemaBase):
    """Listado de toda la configuración (vista admin)."""

    items: list[ConfiguracionPublic]
