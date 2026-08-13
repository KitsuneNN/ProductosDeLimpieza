# -*- coding: utf-8 -*-
"""Modelo Categoria (ARQ-T1)."""
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .producto import Producto


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    orden: Mapped[int] = mapped_column(server_default="0", nullable=False)

    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")
