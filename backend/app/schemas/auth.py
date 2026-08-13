# -*- coding: utf-8 -*-
"""Schemas de autenticación y usuario (ARQ-T2)."""
from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field

from .common import ROL_USUARIO, SchemaBase


class RegistroRequest(SchemaBase):
    nombre: str = Field(min_length=2, max_length=120)
    telefono: str = Field(min_length=6, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(SchemaBase):
    email: EmailStr
    password: str = Field(max_length=72)


class UsuarioPublic(SchemaBase):
    id: int
    nombre: str
    telefono: str
    email: EmailStr
    rol: ROL_USUARIO
    creado_en: datetime


class TokenResponse(SchemaBase):
    access_token: str
    token_type: Literal["bearer"]
    usuario: UsuarioPublic
