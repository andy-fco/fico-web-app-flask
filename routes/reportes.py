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

        transacciones = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.fecha >= desde,
            Transaccion.fecha <= hasta,
        ).all()

        ingresos = sum(float(t.monto) for t in transacciones if t.tipo == "ingreso")
        egresos  = sum(float(t.monto) for t in transacciones if t.tipo == "egreso")
        ahorro   = ingresos - egresos

        por_cat = defaultdict(float)
        for t in transacciones:
            if t.tipo == "egreso":
                por_cat[t.categoria] += float(t.monto)

        total_egresos = sum(por_cat.values()) or 1
        categorias_data = [
            {
                "nombre": nombre,
                "monto":  monto,
                "pct":    round((monto / total_egresos) * 100, 1),
            }
            for nombre, monto in sorted(por_cat.items(), key=lambda x: x[1], reverse=True)
        ]

        mayor_categoria = categorias_data[0] if categorias_data else None
        total_transacciones = len(transacciones)
        total_ing = sum(1 for t in transacciones if t.tipo == "ingreso")
        total_eg  = sum(1 for t in transacciones if t.tipo == "egreso")
        dias_periodo = max((hasta - desde).days, 1)
        promedio_diario = round(egresos / dias_periodo, 2)
        pct_ahorro = round((ahorro / ingresos) * 100, 1) if ingresos > 0 else 0
        pct_egresos = round((egresos / ingresos) * 100, 1) if ingresos > 0 else 0

        hoy = date.today()
        evolucion = []
        max_ahorro = 1

        for i in range(5, -1, -1):
            mes  = (hoy.month - i - 1) % 12 + 1
            anio = hoy.year - ((hoy.month - i - 1) // 12)
            d    = date(anio, mes, 1)
            h    = date(anio, mes, 28 if mes == 2 else 30 if mes in [4,6,9,11] else 31)

            transacciones_mes = Transaccion.query.filter(
                Transaccion.id_usuario == usuario.id_usuario,
                Transaccion.fecha >= d,
                Transaccion.fecha <= h,
            ).all()

            ing_mes = sum(float(t.monto) for t in transacciones_mes if t.tipo == "ingreso")
            eg_mes  = sum(float(t.monto) for t in transacciones_mes if t.tipo == "egreso")
            ah_mes  = ing_mes - eg_mes

            evolucion.append({
                "mes":    d.strftime("%b"),
                "ahorro": ah_mes,
                "actual": i == 0,
            })

            if ah_mes > max_ahorro:
                max_ahorro = ah_mes

        for e in evolucion:
            e["pct_barra"] = round((e["ahorro"] / max_ahorro) * 100, 1) if max_ahorro > 0 else 0

        return render_template(
            "dashboard/reportes.html",
            periodo=periodo,
            ingresos=ingresos,
            egresos=egresos,
            ahorro=ahorro,
            pct_ahorro=pct_ahorro,
            pct_egresos=pct_egresos,
            promedio_diario=promedio_diario,
            categorias_data=categorias_data,
            mayor_categoria=mayor_categoria,
            total_transacciones=total_transacciones,
            total_ing=total_ing,
            total_eg=total_eg,
            evolucion=evolucion,
        )

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
            transacciones = Transaccion.query.filter(
                Transaccion.id_usuario == usuario.id_usuario,
                Transaccion.fecha >= desde,
                Transaccion.fecha <= hasta,
            ).all()
            resultado.append({
                "mes":      desde.strftime("%b"),
                "ingresos": sum(float(t.monto) for t in transacciones if t.tipo == "ingreso"),
                "egresos":  sum(float(t.monto) for t in transacciones if t.tipo == "egreso"),
            })
        return jsonify(resultado)

    @app.route("/api/reportes/categorias")
    @login_required
    def api_categorias_reporte():
        usuario      = get_usuario_actual()
        desde, hasta = get_rango(request.args.get("periodo", "mes"))
        transacciones = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.tipo == "egreso",
            Transaccion.fecha >= desde,
            Transaccion.fecha <= hasta,
        ).all()
        por_cat = defaultdict(float)
        for t in transacciones:
            por_cat[t.categoria] += float(t.monto)
        return jsonify(por_cat)