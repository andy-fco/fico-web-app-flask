from flask import Blueprint, request, render_template, jsonify
from app.models.transaccion import Transaccion
from app.routes import login_required, get_usuario_actual
from datetime import date
from collections import defaultdict

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


def _get_rango(periodo: str) -> tuple[date, date]:
    hoy = date.today()
    if periodo == "semana":
        desde = hoy.replace(day=hoy.day - hoy.weekday())
    elif periodo == "año":
        desde = hoy.replace(month=1, day=1)
    else:  # mes (default)
        desde = hoy.replace(day=1)
    return desde, hoy


@reportes_bp.route("/")
@login_required
def index():
    usuario = get_usuario_actual()
    periodo = request.args.get("periodo", "mes")
    desde, hasta = _get_rango(periodo)

    transacciones = Transaccion.query.filter(
        Transaccion.id_usuario == usuario.id_usuario,
        Transaccion.fecha >= desde,
        Transaccion.fecha <= hasta,
    ).all()

    ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    egresos  = sum(t.monto for t in transacciones if t.tipo == "egreso")
    ahorro   = ingresos - egresos

    # Distribución por categoría
    por_categoria = defaultdict(float)
    for t in transacciones:
        if t.tipo == "egreso" and t.categoria:
            por_categoria[t.categoria.nombre] += t.monto

    return render_template(
        "reportes/index.html",
        periodo=periodo,
        ingresos=ingresos,
        egresos=egresos,
        ahorro=ahorro,
        por_categoria=dict(por_categoria),
    )


@reportes_bp.route("/api/evolucion")
@login_required
def api_evolucion():
    """Datos de los últimos 6 meses para el gráfico de líneas."""
    usuario = get_usuario_actual()
    hoy     = date.today()

    resultado = []
    for i in range(5, -1, -1):
        # mes i meses atrás
        mes   = (hoy.month - i - 1) % 12 + 1
        anio  = hoy.year - ((hoy.month - i - 1) // 12)
        desde = date(anio, mes, 1)
        hasta_dia = 28 if mes == 2 else 30 if mes in [4,6,9,11] else 31
        hasta = date(anio, mes, hasta_dia)

        txs = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.fecha >= desde,
            Transaccion.fecha <= hasta,
        ).all()

        resultado.append({
            "mes":      desde.strftime("%b"),
            "ingresos": sum(t.monto for t in txs if t.tipo == "ingreso"),
            "egresos":  sum(t.monto for t in txs if t.tipo == "egreso"),
        })

    return jsonify(resultado)


@reportes_bp.route("/api/categorias")
@login_required
def api_categorias():
    """Datos de gastos por categoría para el gráfico de dona."""
    usuario = get_usuario_actual()
    periodo = request.args.get("periodo", "mes")
    desde, hasta = _get_rango(periodo)

    transacciones = Transaccion.query.filter(
        Transaccion.id_usuario == usuario.id_usuario,
        Transaccion.tipo == "egreso",
        Transaccion.fecha >= desde,
        Transaccion.fecha <= hasta,
    ).all()

    por_categoria = defaultdict(float)
    for t in transacciones:
        nombre = t.categoria.nombre if t.categoria else "Sin categoria"
        por_categoria[nombre] += t.monto

    return jsonify(por_categoria)
