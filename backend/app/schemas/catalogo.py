# -*- coding: utf-8 -*-
"""Schemas del catálogo de cliente (ARQ-T2)."""
from .categoria import CategoriaPublic
from .common import SchemaBase
from .producto import ProductoClientePublic


class CategoriasResponse(SchemaBase):
    items: list[CategoriaPublic]


class CatalogoResponse(SchemaBase):
    items: list[ProductoClientePublic]
    page: int
    page_size: int
    total: int
