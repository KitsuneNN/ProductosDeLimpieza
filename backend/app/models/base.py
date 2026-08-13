# -*- coding: utf-8 -*-
"""Base declarativa y mixins compartidos por todos los modelos (ARQ-T1)."""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos SQLAlchemy 2.x."""


class TimestampMixin:
    """Agrega la columna `creado_en` con default del servidor."""

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
