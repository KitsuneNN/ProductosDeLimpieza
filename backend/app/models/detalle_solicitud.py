# -*- coding: utf-8 -*-
"""Modelo DetalleSolicitud — líneas de una solicitud (ARQ-T1)."""
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .producto import Producto
    from .solicitud import Solicitud


class DetalleSolicitud(Base):
    __tablename__ = "detalle_solicitud"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        CheckConstraint(
            "precio_unitario >= 0", name="ck_detalle_precio_no_negativo"
        ),
        UniqueConstraint(
            "solicitud_id", "producto_id", name="uq_detalle_solicitud_producto"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    solicitud_id: Mapped[int] = mapped_column(
        ForeignKey("solicitudes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    solicitud: Mapped["Solicitud"] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship()
