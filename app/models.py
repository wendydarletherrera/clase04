from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin

from app import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nombre_completo = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="analista", index=True)
    estado = db.Column(db.String(20), nullable=False, default="activo", index=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)

    accesos = db.relationship("BitacoraAcceso", back_populates="usuario", lazy="dynamic")

    @property
    def is_active(self) -> bool:
        return self.estado == "activo"

    def has_role(self, role: str) -> bool:
        return self.rol == role


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    id_venta_csv = db.Column(db.Integer, unique=True, nullable=False, index=True)
    fecha_venta = db.Column(db.Date, nullable=False, index=True)
    hora_venta = db.Column(db.Time, nullable=False)
    canal_venta = db.Column(db.String(40), nullable=False, index=True)
    sucursal = db.Column(db.String(120), nullable=False, index=True)
    region_sucursal = db.Column(db.String(80), nullable=False, index=True)
    id_cliente = db.Column(db.Integer, nullable=False, index=True)
    nombre_cliente = db.Column(db.String(160), nullable=False)
    tipo_cliente = db.Column(db.String(80), nullable=False, index=True)
    segmento_cliente = db.Column(db.String(100), nullable=False, index=True)
    ciudad_cliente = db.Column(db.String(100), nullable=False, index=True)
    zona_cliente = db.Column(db.String(100), nullable=False, index=True)
    nombre_producto = db.Column(db.String(180), nullable=False, index=True)
    categoria_producto = db.Column(db.String(100), nullable=False, index=True)
    linea_producto = db.Column(db.String(120), nullable=False, index=True)
    presentacion = db.Column(db.String(80), nullable=False)
    origen_cafe = db.Column(db.String(80), nullable=False, index=True)
    tipo_tueste = db.Column(db.String(80), nullable=False, index=True)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    descuento_porcentaje = db.Column(db.Numeric(5, 2), nullable=False)
    total_bruto = db.Column(db.Numeric(14, 2), nullable=False)
    total_descuento = db.Column(db.Numeric(14, 2), nullable=False)
    total_neto = db.Column(db.Numeric(14, 2), nullable=False, index=True)


class BitacoraAcceso(db.Model):
    __tablename__ = "bitacora_acceso"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip = db.Column(db.String(64))
    accion = db.Column(db.String(80), nullable=False)
    detalle = db.Column(db.String(255))

    usuario = db.relationship("Usuario", back_populates="accesos")
