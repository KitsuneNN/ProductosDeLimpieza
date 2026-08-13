# -*- coding: utf-8 -*-
"""Schemas de categorías (ARQ-T2)."""
from pydantic import Field

from .common import SchemaBase


class CategoriaPublic(SchemaBase):
    id: int
    nombre: str
    orden: int


class CategoriaCreate(SchemaBase):
    nombre: str = Field(min_length=2, max_length=80)
    orden: int = 0


class CategoriaUpdate(SchemaBase):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    orden: int | None = None
