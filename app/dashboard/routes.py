from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from sqlalchemy import and_, desc, distinct, func, select

from app import db
from app.models import Venta

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/ejecutivo")
@login_required
def ejecutivo():
    return render_template("dashboard1.html", title="Dashboard Ejecutivo", dashboard="ejecutivo")


@dashboard_bp.route("/clientes")
@login_required
def clientes():
    return render_template("dashboard2.html", title="Dashboard Clientes", dashboard="clientes")


@dashboard_bp.route("/productos")
@login_required
def productos():
    return render_template("dashboard3.html", title="Dashboard Productos", dashboard="productos")


@dashboard_bp.route("/api/filtros")
@login_required
def api_filtros():
    fields = [
        "canal_venta",
        "sucursal",
        "region_sucursal",
        "tipo_cliente",
        "segmento_cliente",
        "ciudad_cliente",
        "zona_cliente",
        "categoria_producto",
        "linea_producto",
        "origen_cafe",
        "tipo_tueste",
    ]
    payload = {}
    for field in fields:
        column = getattr(Venta, field)
        payload[field] = [
            value
            for value in db.session.execute(select(column).distinct().order_by(column.asc())).scalars().all()
            if value is not None
        ]

    year_expr = func.extract("year", Venta.fecha_venta).label("anio")
    month_expr = func.extract("month", Venta.fecha_venta).label("mes")
    payload["anio"] = [
        int(value)
        for value in db.session.execute(select(year_expr).distinct().order_by(year_expr)).scalars().all()
        if value is not None
    ]
    payload["mes"] = [
        int(value)
        for value in db.session.execute(select(month_expr).distinct().order_by(month_expr)).scalars().all()
        if value is not None
    ]

    min_date, max_date = db.session.query(func.min(Venta.fecha_venta), func.max(Venta.fecha_venta)).one()
    payload["fecha_min"] = min_date.isoformat() if min_date else ""
    payload["fecha_max"] = max_date.isoformat() if max_date else ""
    return jsonify(payload)


@dashboard_bp.route("/api/ejecutivo")
@login_required
def api_ejecutivo():
    query = _filtered_query(["anio", "mes", "sucursal", "region_sucursal", "canal_venta"])
    kpis = _executive_kpis(query)
    charts = [
        _monthly_chart(query, "Ventas por mes", "line"),
        _group_sum_chart(query, Venta.sucursal, "Ventas por sucursal", "bar"),
        _group_sum_chart(query, Venta.canal_venta, "Ventas por canal", "doughnut"),
        _group_sum_chart(query, Venta.region_sucursal, "Ventas por region", "bar"),
    ]
    table = _summary_table(
        query,
        [Venta.sucursal, Venta.region_sucursal, Venta.canal_venta],
        ["Sucursal", "Region", "Canal"],
    )
    return jsonify({"kpis": kpis, "charts": charts, "table": table})


@dashboard_bp.route("/api/clientes")
@login_required
def api_clientes():
    query = _filtered_query(
        ["anio", "mes", "tipo_cliente", "segmento_cliente", "ciudad_cliente", "zona_cliente"]
    )
    kpis = _client_kpis(query)
    charts = [
        _group_sum_chart(query, Venta.tipo_cliente, "Ventas por tipo de cliente", "doughnut"),
        _group_sum_chart(query, Venta.segmento_cliente, "Ventas por segmento", "bar"),
        _group_sum_chart(query, Venta.ciudad_cliente, "Top ciudades", "bar", limit=10),
        _group_sum_chart(query, Venta.zona_cliente, "Distribucion por zona", "pie"),
    ]
    table = _summary_table(
        query,
        [Venta.tipo_cliente, Venta.segmento_cliente, Venta.ciudad_cliente],
        ["Tipo", "Segmento", "Ciudad"],
    )
    return jsonify({"kpis": kpis, "charts": charts, "table": table})


@dashboard_bp.route("/api/productos")
@login_required
def api_productos():
    query = _filtered_query(
        [
            "anio",
            "mes",
            "categoria_producto",
            "linea_producto",
            "origen_cafe",
            "tipo_tueste",
            "sucursal",
        ]
    )
    kpis = _product_kpis(query)
    charts = [
        _group_sum_chart(query, Venta.categoria_producto, "Ventas por categoria", "bar"),
        _group_sum_chart(query, Venta.linea_producto, "Ventas por linea", "bar"),
        _group_sum_chart(query, Venta.origen_cafe, "Ventas por origen", "doughnut"),
        _group_sum_chart(query, Venta.tipo_tueste, "Ventas por tueste", "pie"),
    ]
    return jsonify({"kpis": kpis, "charts": charts, "table": _olap_table(query)})


@dashboard_bp.route("/api/olap")
@login_required
def api_olap():
    query = _filtered_query(
        [
            "anio",
            "mes",
            "categoria_producto",
            "linea_producto",
            "origen_cafe",
            "tipo_tueste",
            "sucursal",
        ]
    )
    return jsonify(_olap_table(query))


def _filtered_query(allowed_filters: list[str]):
    query = Venta.query
    conditions = []

    if "anio" in allowed_filters and request.args.get("anio") not in (None, "", "all"):
        year = _parse_int(request.args["anio"])
        if year:
            conditions.append(func.extract("year", Venta.fecha_venta) == year)
    if "mes" in allowed_filters and request.args.get("mes") not in (None, "", "all"):
        month = _parse_int(request.args["mes"])
        if month:
            conditions.append(func.extract("month", Venta.fecha_venta) == month)

    field_map = {
        "sucursal": Venta.sucursal,
        "region_sucursal": Venta.region_sucursal,
        "canal_venta": Venta.canal_venta,
        "tipo_cliente": Venta.tipo_cliente,
        "segmento_cliente": Venta.segmento_cliente,
        "ciudad_cliente": Venta.ciudad_cliente,
        "zona_cliente": Venta.zona_cliente,
        "categoria_producto": Venta.categoria_producto,
        "linea_producto": Venta.linea_producto,
        "origen_cafe": Venta.origen_cafe,
        "tipo_tueste": Venta.tipo_tueste,
    }
    for field, column in field_map.items():
        value = request.args.get(field)
        if field in allowed_filters and value and value != "all":
            conditions.append(column == value)

    if conditions:
        query = query.filter(and_(*conditions))
    return query


def _parse_int(value: str):
    try:
        return int(value)
    except ValueError:
        return None


def _scalar(query, expression, default=0):
    value = query.with_entities(expression).scalar()
    return default if value is None else value


def _money(value) -> str:
    return f"Bs {_to_float(value):,.2f}"


def _number(value) -> str:
    return f"{_to_float(value):,.0f}"


def _to_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _top_label(query, column) -> str:
    row = (
        query.with_entities(column.label("label"), func.sum(Venta.total_neto).label("total"))
        .group_by(column)
        .order_by(desc("total"))
        .first()
    )
    return row.label if row else "Sin datos"


def _executive_kpis(query) -> list[dict[str, str]]:
    total_neto = _scalar(query, func.sum(Venta.total_neto))
    total_bruto = _scalar(query, func.sum(Venta.total_bruto))
    cantidad = _scalar(query, func.sum(Venta.cantidad))
    ticket = _scalar(query, func.avg(Venta.total_neto))
    descuento = _scalar(query, func.sum(Venta.total_descuento))
    clientes = _scalar(query, func.count(distinct(Venta.id_cliente)))
    return [
        {"title": "Ventas netas", "value": _money(total_neto), "icon": "fa-chart-line", "tone": "gold"},
        {"title": "Ventas brutas", "value": _money(total_bruto), "icon": "fa-cash-register", "tone": "coffee"},
        {"title": "Cantidad total", "value": _number(cantidad), "icon": "fa-boxes-stacked", "tone": "olive"},
        {"title": "Ticket promedio", "value": _money(ticket), "icon": "fa-receipt", "tone": "caramel"},
        {"title": "Descuento total", "value": _money(descuento), "icon": "fa-tags", "tone": "muted"},
        {"title": "Clientes unicos", "value": _number(clientes), "icon": "fa-users", "tone": "green"},
    ]


def _client_kpis(query) -> list[dict[str, str]]:
    clientes = _scalar(query, func.count(distinct(Venta.id_cliente)))
    ticket = _scalar(query, func.avg(Venta.total_neto))
    descuento = _scalar(query, func.avg(Venta.descuento_porcentaje))
    top_segment = _top_label(query, Venta.segmento_cliente)
    return [
        {"title": "Clientes unicos", "value": _number(clientes), "icon": "fa-users", "tone": "gold"},
        {"title": "Ticket promedio", "value": _money(ticket), "icon": "fa-receipt", "tone": "coffee"},
        {"title": "Segmento top", "value": top_segment, "icon": "fa-layer-group", "tone": "olive"},
        {"title": "Descuento promedio", "value": f"{_to_float(descuento):,.1f}%", "icon": "fa-percent", "tone": "caramel"},
    ]


def _product_kpis(query) -> list[dict[str, str]]:
    producto = _top_label(query, Venta.nombre_producto)
    categoria = _top_label(query, Venta.categoria_producto)
    cantidad = _scalar(query, func.sum(Venta.cantidad))
    ventas = _scalar(query, func.sum(Venta.total_neto))
    return [
        {"title": "Producto top", "value": producto, "icon": "fa-mug-hot", "tone": "gold"},
        {"title": "Categoria top", "value": categoria, "icon": "fa-sitemap", "tone": "coffee"},
        {"title": "Cantidad total", "value": _number(cantidad), "icon": "fa-boxes-stacked", "tone": "olive"},
        {"title": "Ventas totales", "value": _money(ventas), "icon": "fa-chart-column", "tone": "caramel"},
    ]


def _monthly_chart(query, title: str, chart_type: str) -> dict:
    year = func.extract("year", Venta.fecha_venta)
    month = func.extract("month", Venta.fecha_venta)
    rows = (
        query.with_entities(
            year.label("anio"),
            month.label("mes"),
            func.sum(Venta.total_neto).label("total"),
        )
        .group_by("anio", "mes")
        .order_by("anio", "mes")
        .all()
    )
    return {
        "title": title,
        "type": chart_type,
        "labels": [f"{int(row.anio)}-{int(row.mes):02d}" for row in rows],
        "data": [_to_float(row.total) for row in rows],
    }


def _group_sum_chart(query, column, title: str, chart_type: str, limit: int | None = None) -> dict:
    grouped = (
        query.with_entities(column.label("label"), func.sum(Venta.total_neto).label("total"))
        .group_by(column)
        .order_by(desc("total"))
    )
    if limit:
        grouped = grouped.limit(limit)
    rows = grouped.all()
    return {
        "title": title,
        "type": chart_type,
        "labels": [row.label for row in rows],
        "data": [_to_float(row.total) for row in rows],
    }


def _summary_table(query, group_columns, labels: list[str]) -> dict:
    rows = (
        query.with_entities(
            *[column.label(f"group_{index}") for index, column in enumerate(group_columns)],
            func.sum(Venta.total_neto).label("ventas_netas"),
            func.sum(Venta.cantidad).label("cantidad"),
            func.count(distinct(Venta.id_cliente)).label("clientes"),
            func.avg(Venta.total_neto).label("ticket_promedio"),
        )
        .group_by(*group_columns)
        .order_by(desc("ventas_netas"))
        .limit(500)
        .all()
    )
    columns = [{"title": label, "data": f"group_{index}"} for index, label in enumerate(labels)]
    columns.extend(
        [
            {"title": "Ventas netas", "data": "ventas_netas"},
            {"title": "Cantidad", "data": "cantidad"},
            {"title": "Clientes", "data": "clientes"},
            {"title": "Ticket promedio", "data": "ticket_promedio"},
        ]
    )
    data = []
    for row in rows:
        item = {f"group_{index}": getattr(row, f"group_{index}") for index in range(len(group_columns))}
        item.update(
            {
                "ventas_netas": _money(row.ventas_netas),
                "cantidad": _number(row.cantidad),
                "clientes": _number(row.clientes),
                "ticket_promedio": _money(row.ticket_promedio),
            }
        )
        data.append(item)
    return {"columns": columns, "rows": data}


def _olap_table(query) -> dict:
    year = func.extract("year", Venta.fecha_venta)
    month = func.extract("month", Venta.fecha_venta)
    rows = (
        query.with_entities(
            year.label("anio"),
            month.label("mes"),
            Venta.sucursal.label("sucursal"),
            Venta.categoria_producto.label("categoria"),
            func.sum(Venta.total_neto).label("ventas_netas"),
            func.sum(Venta.cantidad).label("cantidad"),
            func.count(distinct(Venta.id_cliente)).label("clientes"),
        )
        .group_by("anio", "mes", Venta.sucursal, Venta.categoria_producto)
        .order_by("anio", "mes", Venta.sucursal, Venta.categoria_producto)
        .limit(1000)
        .all()
    )
    return {
        "columns": [
            {"title": "Anio", "data": "anio"},
            {"title": "Mes", "data": "mes"},
            {"title": "Sucursal", "data": "sucursal"},
            {"title": "Categoria", "data": "categoria"},
            {"title": "Ventas netas", "data": "ventas_netas"},
            {"title": "Cantidad", "data": "cantidad"},
            {"title": "Clientes", "data": "clientes"},
        ],
        "rows": [
            {
                "anio": int(row.anio),
                "mes": int(row.mes),
                "sucursal": row.sucursal,
                "categoria": row.categoria,
                "ventas_netas": _money(row.ventas_netas),
                "cantidad": _number(row.cantidad),
                "clientes": _number(row.clientes),
            }
            for row in rows
        ],
    }
