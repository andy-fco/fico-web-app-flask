from flask import request, render_template, jsonify
from models.transaccion import Transaccion
from routes import login_required, get_usuario_actual
from datetime import date
from collections import defaultdict


def get_rango(periodo):
    hoy = date.today()
    if periodo == "semana":
        desde = hoy.replace(day=hoy.day - hoy.weekday())
    elif periodo == "año":
        desde = hoy.replace(month=1, day=1)
    else:
        desde = hoy.replace(day=1)
    return desde, hoy


def register_routes(app):

    @app.route("/dashboard/reportes")
    @login_required
    def reportes():
        usuario      = get_usuario_actual()
        periodo      = request.args.get("periodo", "mes")
        desde, hasta = get_rango(periodo)
        txs          = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.fecha >= desde,
            Transaccion.fecha <= hasta,
        ).all()
        ingresos  = sum(t.monto for t in txs if t.tipo == "ingreso")
        egresos   = sum(t.monto for t in txs if t.tipo == "egreso")
        por_cat   = defaultdict(float)
        for t in txs:
            if t.tipo == "egreso" and t.categoria:
                por_cat[t.categoria.nombre] += t.monto
        return render_template("dashboard/reportes.html",
                               periodo=periodo, ingresos=ingresos, egresos=egresos,
                               ahorro=ingresos - egresos, por_categoria=dict(por_cat))

    @app.route("/api/reportes/evolucion")
    @login_required
    def api_evolucion():
        usuario   = get_usuario_actual()
        hoy       = date.today()
        resultado = []
        for i in range(5, -1, -1):
            mes   = (hoy.month - i - 1) % 12 + 1
            anio  = hoy.year - ((hoy.month - i - 1) // 12)
            desde = date(anio, mes, 1)
            hasta = date(anio, mes, 28 if mes == 2 else 30 if mes in [4,6,9,11] else 31)
            txs   = Transaccion.query.filter(
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

    @app.route("/api/reportes/categorias")
    @login_required
    def api_categorias_reporte():
        usuario      = get_usuario_actual()
        desde, hasta = get_rango(request.args.get("periodo", "mes"))
        txs          = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.tipo == "egreso",
            Transaccion.fecha >= desde,
            Transaccion.fecha <= hasta,
        ).all()
        por_cat = defaultdict(float)
        for t in txs:
            por_cat[t.categoria.nombre if t.categoria else "Sin categoria"] += t.monto
        return jsonify(por_cat)
