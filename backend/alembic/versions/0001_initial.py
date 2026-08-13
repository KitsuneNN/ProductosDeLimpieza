# -*- coding: utf-8 -*-
"""Migración inicial — esquema completo (ARQ-T1, DDL CONGELADO).

DDL explícito y autocontenido: NO depende del código de la app, por lo que
esta migración queda congelada en el tiempo aunque los modelos evolucionen
(buena higiene de migraciones).

Rollback: elimina todas las tablas en orden inverso de dependencia.
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- usuarios ---
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", sa.String(length=20), server_default="cliente", nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("rol IN ('cliente', 'admin')", name="ck_usuarios_rol"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    # --- categorias ---
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=80), nullable=False),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categorias_nombre", "categorias", ["nombre"], unique=True)

    # --- productos ---
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("precio", sa.Numeric(12, 2), nullable=False),
        sa.Column("stock_actual", sa.Integer(), server_default="0", nullable=False),
        sa.Column("imagen_url", sa.String(length=500), nullable=True),
        sa.Column("estado", sa.String(length=20), server_default="activo", nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("stock_actual >= 0", name="ck_productos_stock_no_negativo"),
        sa.CheckConstraint("precio >= 0", name="ck_productos_precio_no_negativo"),
        sa.CheckConstraint("estado IN ('activo', 'pausado')", name="ck_productos_estado"),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_productos_categoria_id", "productos", ["categoria_id"])
    op.create_index("ix_productos_nombre", "productos", ["nombre"])

    # --- solicitudes ---
    op.create_table(
        "solicitudes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), server_default="pendiente", nullable=False),
        sa.Column("total", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("pagada_en", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'pagada', 'cancelada')",
            name="ck_solicitudes_estado",
        ),
        sa.CheckConstraint("total >= 0", name="ck_solicitudes_total_no_negativo"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_solicitudes_usuario_id", "solicitudes", ["usuario_id"])

    # --- detalle_solicitud ---
    op.create_table(
        "detalle_solicitud",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("solicitud_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        sa.CheckConstraint("precio_unitario >= 0", name="ck_detalle_precio_no_negativo"),
        sa.ForeignKeyConstraint(
            ["solicitud_id"], ["solicitudes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"], ["productos.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "solicitud_id", "producto_id", name="uq_detalle_solicitud_producto"
        ),
    )
    op.create_index(
        "ix_detalle_solicitud_solicitud_id", "detalle_solicitud", ["solicitud_id"]
    )
    op.create_index(
        "ix_detalle_solicitud_producto_id", "detalle_solicitud", ["producto_id"]
    )

    # --- configuracion ---
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.String(length=80), nullable=False),
        sa.Column("valor", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("clave"),
    )


def downgrade() -> None:
    op.drop_table("configuracion")
    op.drop_table("detalle_solicitud")
    op.drop_table("solicitudes")
    op.drop_table("productos")
    op.drop_table("categorias")
    op.drop_table("usuarios")
