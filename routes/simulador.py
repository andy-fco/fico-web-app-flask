from flask import request, render_template, jsonify
from extensions import db
from models.proyeccion import ProyeccionFinanciera
from models.simulacion_if import SimulacionIF
from routes import login_required, get_usuario_actual


def register_routes(app):

    @app.route("/dashboard/proyecciones")
    @login_required
    def proyecciones():
        usuario = get_usuario_actual()
        return render_template("dashboard/proyecciones.html", proyecciones=usuario.proyecciones)

    @app.route("/dashboard/proyecciones/calcular", methods=["POST"])
    @login_required
    def calcular_proyeccion():
        usuario   = get_usuario_actual()
        horizonte = request.form.get("horizonte")
        p = ProyeccionFinanciera(
            id_usuario       = usuario.id_usuario,
            ahorro_mensual   = request.form.get("ahorro_mensual",   type=float, default=0),
            capital_inicial  = request.form.get("capital_inicial",  type=float, default=0),
            tasa_interes     = request.form.get("tasa_interes",     type=float, default=0),
            objetivo_capital = request.form.get("objetivo_capital", type=float) or None,
            horizonte        = horizonte,
        )
        meses = {"1a": 12, "5a": 60, "10a": 120}.get(horizonte, 12)
        p.capital_proyectado = p.calcular_capital_futuro(meses)
        db.session.add(p)
        db.session.commit()
        return render_template("dashboard/proyecciones.html",
                               proyecciones=usuario.proyecciones,
                               resultado=p, meses=meses,
                               tiempo_objetivo=p.calcular_tiempo_objetivo())

    @app.route("/api/proyeccion", methods=["POST"])
    @login_required
    def api_proyeccion():
        data = request.get_json()
        p    = ProyeccionFinanciera(
            ahorro_mensual  = float(data.get("ahorro_mensual", 0)),
            capital_inicial = float(data.get("capital_inicial", 0)),
            tasa_interes    = float(data.get("tasa_interes", 0)),
        )
        return jsonify({
            "1_anio":   p.calcular_capital_futuro(12),
            "5_anios":  p.calcular_capital_futuro(60),
            "10_anios": p.calcular_capital_futuro(120),
        })

    @app.route("/dashboard/independencia")
    @login_required
    def independencia():
        usuario = get_usuario_actual()
        return render_template("dashboard/independencia.html", simulaciones=usuario.simulaciones)

    @app.route("/dashboard/independencia/calcular", methods=["POST"])
    @login_required
    def calcular_independencia():
        usuario = get_usuario_actual()
        s = SimulacionIF(
            id_usuario        = usuario.id_usuario,
            gastos_mensuales  = request.form.get("gastos_mensuales",  type=float, default=0),
            ahorro_disponible = request.form.get("ahorro_disponible", type=float, default=0),
            tasa_inversion    = request.form.get("tasa_inversion",    type=float, default=0),
            edad_actual       = request.form.get("edad_actual",       type=int,   default=25),
            edad_objetivo     = request.form.get("edad_objetivo",     type=int,   default=60),
            capital_inicial   = request.form.get("capital_inicial",   type=float, default=0),
        )
        s.capital_objetivo = s.calcular_capital_objetivo()
        db.session.add(s)
        db.session.commit()
        return render_template("dashboard/independencia.html",
                               simulaciones=usuario.simulaciones,
                               resultado=s,
                               inversion_mensual=s.calcular_inversion_mensual(),
                               tiempo_meses=s.calcular_tiempo())
