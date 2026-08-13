# -*- coding: utf-8 -*-
"""Modelo Usuario — roles: cliente | admin (ARQ-T1)."""
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .solicitud import Solicitud

ROLES_VALIDOS = ("cliente", "admin")


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("rol IN ('cliente', 'admin')", name="ck_usuarios_rol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), server_default="cliente", nullable=False)

    solicitudes: Mapped[list["Solicitud"]] = relationship(back_populates="usuario")
