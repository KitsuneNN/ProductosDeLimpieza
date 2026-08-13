# -*- coding: utf-8 -*-
"""Modelo Configuracion — pares clave/valor (ARQ-T1).

Claves conocidas (MVP):
- `umbral_pocas_unidades` → entero, default "5": a partir de cuántas unidades
  un producto pasa a mostrarse como "Pocas unidades" para el cliente.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

CLAVES_CONOCIDAS = ("umbral_pocas_unidades",)


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(String(80), primary_key=True)
    valor: Mapped[str] = mapped_column(String(255), nullable=False)
