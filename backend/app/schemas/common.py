# -*- coding: utf-8 -*-
"""Tipos compartidos de los schemas (ARQ-T2)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------- enums/union
DISPONIBILIDAD = Literal["disponible", "pocas", "sin_stock"]
ESTADO_PRODUCTO = Literal["activo", "pausado"]
ESTADO_SOLICITUD = Literal["pendiente", "pagada", "cancelada"]
ROL_USUARIO = Literal["cliente", "admin"]


class SchemaBase(BaseModel):
    """Base común: permite construir schemas desde ORM."""

    model_config = ConfigDict(from_attributes=True)
