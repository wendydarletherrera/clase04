from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import select

from app import db
from app.models import Venta

EXPECTED_COLUMNS = [
    "id_venta",
    "fecha_venta",
    "hora_venta",
    "canal_venta",
    "sucursal",
    "region_sucursal",
    "id_cliente",
    "nombre_cliente",
    "tipo_cliente",
    "segmento_cliente",
    "ciudad_cliente",
    "zona_cliente",
    "nombre_producto",
    "categoria_producto",
    "linea_producto",
    "presentacion",
    "origen_cafe",
    "tipo_tueste",
    "precio_unitario",
    "cantidad",
    "descuento_porcentaje",
    "total_bruto",
    "total_descuento",
    "total_neto",
]


@dataclass
class ImportResult:
    inserted: int = 0
    skipped: int = 0
    errors: list[dict[str, str | int]] = field(default_factory=list)


def import_sales_csv(path: str | Path, batch_size: int = 500) -> ImportResult:
    csv_path = Path(path)
    result = ImportResult()
    if not csv_path.exists():
        result.errors.append({"line": 0, "error": f"No existe el archivo: {csv_path}"})
        return result

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != EXPECTED_COLUMNS:
            result.errors.append(
                {
                    "line": 1,
                    "error": "Columnas invalidas. Se esperaba: " + ", ".join(EXPECTED_COLUMNS),
                }
            )
            return result

        rows = list(reader)

    csv_ids = set()
    for row in rows:
        try:
            csv_ids.add(_to_int(row["id_venta"]))
        except (ValueError, TypeError):
            continue
    existing_ids = set(
        db.session.scalars(select(Venta.id_venta_csv).where(Venta.id_venta_csv.in_(csv_ids))).all()
    )

    pending: list[Venta] = []
    seen_in_file: set[int] = set()

    for index, row in enumerate(rows, start=2):
        try:
            venta = _row_to_sale(row)
        except (ValueError, InvalidOperation) as exc:
            result.errors.append({"line": index, "error": str(exc)})
            continue

        if venta.id_venta_csv in existing_ids or venta.id_venta_csv in seen_in_file:
            result.skipped += 1
            continue

        seen_in_file.add(venta.id_venta_csv)
        pending.append(venta)

        if len(pending) >= batch_size:
            db.session.add_all(pending)
            db.session.flush()
            result.inserted += len(pending)
            pending.clear()

    if pending:
        db.session.add_all(pending)
        db.session.flush()
        result.inserted += len(pending)

    db.session.commit()
    return result


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _to_int(value: str | None) -> int:
    cleaned = _clean(value)
    if cleaned == "":
        raise ValueError("Valor entero vacio")
    return int(cleaned)


def _to_decimal(value: str | None) -> Decimal:
    cleaned = _clean(value).replace(",", ".")
    if cleaned == "":
        raise ValueError("Valor decimal vacio")
    return Decimal(cleaned)


def _row_to_sale(row: dict[str, str]) -> Venta:
    return Venta(
        id_venta_csv=_to_int(row["id_venta"]),
        fecha_venta=datetime.strptime(_clean(row["fecha_venta"]), "%Y-%m-%d").date(),
        hora_venta=datetime.strptime(_clean(row["hora_venta"]), "%H:%M").time(),
        canal_venta=_clean(row["canal_venta"]),
        sucursal=_clean(row["sucursal"]),
        region_sucursal=_clean(row["region_sucursal"]),
        id_cliente=_to_int(row["id_cliente"]),
        nombre_cliente=_clean(row["nombre_cliente"]),
        tipo_cliente=_clean(row["tipo_cliente"]),
        segmento_cliente=_clean(row["segmento_cliente"]),
        ciudad_cliente=_clean(row["ciudad_cliente"]),
        zona_cliente=_clean(row["zona_cliente"]),
        nombre_producto=_clean(row["nombre_producto"]),
        categoria_producto=_clean(row["categoria_producto"]),
        linea_producto=_clean(row["linea_producto"]),
        presentacion=_clean(row["presentacion"]),
        origen_cafe=_clean(row["origen_cafe"]),
        tipo_tueste=_clean(row["tipo_tueste"]),
        precio_unitario=_to_decimal(row["precio_unitario"]),
        cantidad=_to_int(row["cantidad"]),
        descuento_porcentaje=_to_decimal(row["descuento_porcentaje"]),
        total_bruto=_to_decimal(row["total_bruto"]),
        total_descuento=_to_decimal(row["total_descuento"]),
        total_neto=_to_decimal(row["total_neto"]),
    )
