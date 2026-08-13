# -*- coding: utf-8 -*-
"""Migración inicial — crea todo el esquema desde los modelos (ARQ-T1).

Estrategia: genera el DDL directo desde `Base.metadata` para garantizar
consistencia EXACTA entre modelos y migración (Regla 5). El rollback elimina
todas las tablas en orden inverso de dependencia.
"""
from alembic import op

from app.models import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
