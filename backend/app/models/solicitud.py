# -*- coding: utf-8 -*-
"""Modelo Solicitud — máquina de estados (ARQ-T1).

pendiente → pagada
pendiente → cancelada
(transiciones implementadas en services; la BD las restringe con CHECK)
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .detalle_solicitud import DetalleSolicitud
    from .usuario import Usuario

ESTADOS_SOLICITUD = ("pendiente", "pagada", "cancelada")


class Solicitud(TimestampMixin, Base):
    __tablename__ = "solicitudes"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'pagada', 'cancelada')",
            name="ck_solicitudes_estado",
        ),
        CheckConstraint("total >= 0", name="ck_solicitudes_total_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="pendiente", nullable=False
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    pagada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="solicitudes")
    detalles: Mapped[list["DetalleSolicitud"]] = relationship(
        back_populates="solicitud", cascade="all, delete-orphan"
    )
