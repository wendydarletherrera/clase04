"""initial schema

Revision ID: 20260420_0001
Revises:
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa

revision = "20260420_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("nombre_completo", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", sa.String(length=20), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("ultimo_acceso", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=False)
    op.create_index(op.f("ix_usuarios_estado"), "usuarios", ["estado"], unique=False)
    op.create_index(op.f("ix_usuarios_rol"), "usuarios", ["rol"], unique=False)
    op.create_index(op.f("ix_usuarios_username"), "usuarios", ["username"], unique=False)

    op.create_table(
        "ventas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_venta_csv", sa.Integer(), nullable=False),
        sa.Column("fecha_venta", sa.Date(), nullable=False),
        sa.Column("hora_venta", sa.Time(), nullable=False),
        sa.Column("canal_venta", sa.String(length=40), nullable=False),
        sa.Column("sucursal", sa.String(length=120), nullable=False),
        sa.Column("region_sucursal", sa.String(length=80), nullable=False),
        sa.Column("id_cliente", sa.Integer(), nullable=False),
        sa.Column("nombre_cliente", sa.String(length=160), nullable=False),
        sa.Column("tipo_cliente", sa.String(length=80), nullable=False),
        sa.Column("segmento_cliente", sa.String(length=100), nullable=False),
        sa.Column("ciudad_cliente", sa.String(length=100), nullable=False),
        sa.Column("zona_cliente", sa.String(length=100), nullable=False),
        sa.Column("nombre_producto", sa.String(length=180), nullable=False),
        sa.Column("categoria_producto", sa.String(length=100), nullable=False),
        sa.Column("linea_producto", sa.String(length=120), nullable=False),
        sa.Column("presentacion", sa.String(length=80), nullable=False),
        sa.Column("origen_cafe", sa.String(length=80), nullable=False),
        sa.Column("tipo_tueste", sa.String(length=80), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("descuento_porcentaje", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("total_bruto", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_descuento", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_neto", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_venta_csv"),
    )
    op.create_index(op.f("ix_ventas_canal_venta"), "ventas", ["canal_venta"], unique=False)
    op.create_index(op.f("ix_ventas_categoria_producto"), "ventas", ["categoria_producto"], unique=False)
    op.create_index(op.f("ix_ventas_ciudad_cliente"), "ventas", ["ciudad_cliente"], unique=False)
    op.create_index(op.f("ix_ventas_fecha_venta"), "ventas", ["fecha_venta"], unique=False)
    op.create_index(op.f("ix_ventas_id_cliente"), "ventas", ["id_cliente"], unique=False)
    op.create_index(op.f("ix_ventas_id_venta_csv"), "ventas", ["id_venta_csv"], unique=False)
    op.create_index(op.f("ix_ventas_linea_producto"), "ventas", ["linea_producto"], unique=False)
    op.create_index(op.f("ix_ventas_nombre_producto"), "ventas", ["nombre_producto"], unique=False)
    op.create_index(op.f("ix_ventas_origen_cafe"), "ventas", ["origen_cafe"], unique=False)
    op.create_index(op.f("ix_ventas_region_sucursal"), "ventas", ["region_sucursal"], unique=False)
    op.create_index(op.f("ix_ventas_segmento_cliente"), "ventas", ["segmento_cliente"], unique=False)
    op.create_index(op.f("ix_ventas_sucursal"), "ventas", ["sucursal"], unique=False)
    op.create_index(op.f("ix_ventas_tipo_cliente"), "ventas", ["tipo_cliente"], unique=False)
    op.create_index(op.f("ix_ventas_tipo_tueste"), "ventas", ["tipo_tueste"], unique=False)
    op.create_index(op.f("ix_ventas_total_neto"), "ventas", ["total_neto"], unique=False)
    op.create_index(op.f("ix_ventas_zona_cliente"), "ventas", ["zona_cliente"], unique=False)

    op.create_table(
        "bitacora_acceso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("fecha_hora", sa.DateTime(), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("accion", sa.String(length=80), nullable=False),
        sa.Column("detalle", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bitacora_acceso_fecha_hora"), "bitacora_acceso", ["fecha_hora"], unique=False)
    op.create_index(op.f("ix_bitacora_acceso_usuario_id"), "bitacora_acceso", ["usuario_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_bitacora_acceso_usuario_id"), table_name="bitacora_acceso")
    op.drop_index(op.f("ix_bitacora_acceso_fecha_hora"), table_name="bitacora_acceso")
    op.drop_table("bitacora_acceso")
    op.drop_index(op.f("ix_ventas_zona_cliente"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_total_neto"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_tipo_tueste"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_tipo_cliente"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_sucursal"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_segmento_cliente"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_region_sucursal"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_origen_cafe"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_nombre_producto"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_linea_producto"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_id_venta_csv"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_id_cliente"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_fecha_venta"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_ciudad_cliente"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_categoria_producto"), table_name="ventas")
    op.drop_index(op.f("ix_ventas_canal_venta"), table_name="ventas")
    op.drop_table("ventas")
    op.drop_index(op.f("ix_usuarios_username"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_rol"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_estado"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
