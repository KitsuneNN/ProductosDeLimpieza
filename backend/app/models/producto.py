# -*- coding: utf-8 -*-
"""Modelo Producto — reglas críticas de inventario (ARQ-T1).

- `stock_actual >= 0` SIEMPRE (CHECK en BD).
- `estado` ∈ {activo, pausado}.
- El stock numérico NUNCA se expone al cliente (solo etiquetas).
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .categoria import Categoria

ESTADOS_PRODUCTO = ("activo", "pausado")


class Producto(TimestampMixin, Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("stock_actual >= 0", name="ck_productos_stock_no_negativo"),
        CheckConstraint("precio >= 0", name="ck_productos_precio_no_negativo"),
        CheckConstraint(
            "estado IN ('activo', 'pausado')", name="ck_productos_estado"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock_actual: Mapped[int] = mapped_column(default=0, nullable=False)
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="productos")
