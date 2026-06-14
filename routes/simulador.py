from flask import request, render_template, flash, redirect, url_for
from extensions import db
from models.simulacion_if import SimulacionIF
from routes import login_required, get_usuario_actual


def obtener_datos_simulacion():
    return {
        "gastos_mensuales": request.form.get("gastos_mensuales", type=float, default=0),
        "ahorro_disponible": request.form.get("ahorro_disponible", type=float, default=0),
        "tasa_rendimiento": request.form.get("tasa_rendimiento", type=float, default=0),
        "tasa_retiro": request.form.get("tasa_retiro", type=float, default=4.0),
        "edad_actual": request.form.get("edad_actual", type=int, default=25),
        "edad_objetivo": request.form.get("edad_objetivo", type=int, default=60),
        "capital_inicial": request.form.get("capital_inicial", type=float, default=0),
        "capital_objetivo": request.form.get("capital_objetivo", type=float) or None,
        "moneda": request.form.get("moneda", default="ARS"),
    }


def validar_datos_simulacion(datos):
    errores = []

    if datos["gastos_mensuales"] <= 0:
        errores.append("El gasto mensual debe ser mayor a cero.")

    if datos["ahorro_disponible"] < 0:
        errores.append("El ahorro mensual no puede ser negativo.")

    if datos["capital_inicial"] < 0:
        errores.append("El capital inicial no puede ser negativo.")

    if datos["tasa_rendimiento"] < 0:
        errores.append("La tasa de rendimiento no puede ser negativa.")

    if datos["tasa_retiro"] <= 0:
        errores.append("La tasa de retiro debe ser mayor a cero.")

    if datos["edad_objetivo"] <= datos["edad_actual"]:
        errores.append("La edad objetivo debe ser mayor a la edad actual.")

    return errores


def crear_simulacion_temporal(datos, usuario=None):
    simulacion = SimulacionIF(
        id_usuario=usuario.id_usuario if usuario else 0,
        gastos_mensuales=datos["gastos_mensuales"],
        ahorro_disponible=datos["ahorro_disponible"],
        tasa_rendimiento=datos["tasa_rendimiento"],
        tasa_retiro=datos["tasa_retiro"],
        edad_actual=datos["edad_actual"],
        edad_objetivo=datos["edad_objetivo"],
        capital_inicial=datos["capital_inicial"],
        capital_objetivo=datos["capital_objetivo"],
        moneda=datos["moneda"],
    )

    simulacion.capital_objetivo = (
        simulacion.capital_objetivo or simulacion.calcular_capital_objetivo()
    )

    return simulacion


def register_routes(app):

    @app.route("/simulador/calcular", methods=["POST"])
    def calcular_simulador_publico():
        datos = obtener_datos_simulacion()
        errores = validar_datos_simulacion(datos)

        if errores:
            for error in errores:
                flash(error, "error")

            return render_template(
                "public/simulador.html",
                valores=datos,
                resultado=None,
                form_action=url_for("calcular_simulador_publico"),
                contexto="publico",
            )

        simulacion = crear_simulacion_temporal(datos)

        return render_template(
            "public/simulador.html",
            valores=datos,
            resultado=simulacion,
            form_action=url_for("calcular_simulador_publico"),
            contexto="publico",
        )


    @app.route("/dashboard/independencia")
    @login_required
    def independencia():
        usuario = get_usuario_actual()

        return render_template(
            "dashboard/independencia.html",
            simulaciones=usuario.simulaciones,
            resultado=None,
            valores={},
            form_action=url_for("calcular_independencia"),
            contexto="dashboard",
        )


    @app.route("/dashboard/independencia/calcular", methods=["POST"])
    @login_required
    def calcular_independencia():
        usuario = get_usuario_actual()
        datos = obtener_datos_simulacion()
        errores = validar_datos_simulacion(datos)

        if errores:
            for error in errores:
                flash(error, "error")

            return render_template(
                "dashboard/independencia.html",
                simulaciones=usuario.simulaciones,
                resultado=None,
                valores=datos,
                form_action=url_for("calcular_independencia"),
                contexto="dashboard",
            )

        simulacion = crear_simulacion_temporal(datos, usuario)

        flash("Simulación calculada. Podés guardarla si querés conservar este escenario.", "success")

        return render_template(
            "dashboard/independencia.html",
            simulaciones=usuario.simulaciones,
            resultado=simulacion,
            valores=datos,
            form_action=url_for("calcular_independencia"),
            contexto="dashboard",
        )


    @app.route("/dashboard/independencia/guardar", methods=["POST"])
    @login_required
    def guardar_independencia():
        usuario = get_usuario_actual()
        datos = obtener_datos_simulacion()
        errores = validar_datos_simulacion(datos)

        if errores:
            for error in errores:
                flash(error, "error")

            return redirect(url_for("independencia"))

        simulacion = crear_simulacion_temporal(datos, usuario)

        db.session.add(simulacion)
        db.session.commit()

        flash("Simulación guardada correctamente.", "success")

        return redirect(url_for("independencia"))
    
    @app.route("/dashboard/independencia/<int:id>/editar")
    @login_required
    def editar_independencia(id):
        usuario = get_usuario_actual()

        simulacion = SimulacionIF.query.filter_by(
            id_simulacion=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        valores = {
            "gastos_mensuales": float(simulacion.gastos_mensuales),
            "ahorro_disponible": float(simulacion.ahorro_disponible),
            "tasa_rendimiento": simulacion.tasa_rendimiento,
            "tasa_retiro": simulacion.tasa_retiro,
            "edad_actual": simulacion.edad_actual,
            "edad_objetivo": simulacion.edad_objetivo,
            "capital_inicial": float(simulacion.capital_inicial),
            "capital_objetivo": float(simulacion.capital_objetivo) if simulacion.capital_objetivo else None,
            "moneda": simulacion.moneda,
        }

        return render_template(
            "dashboard/independencia.html",
            simulaciones=usuario.simulaciones,
            resultado=simulacion,
            valores=valores,
            form_action=url_for("calcular_independencia"),
            contexto="dashboard",
        )
        
    @app.route("/dashboard/independencia/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_independencia(id):
        usuario = get_usuario_actual()

        simulacion = SimulacionIF.query.filter_by(
            id_simulacion=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        db.session.delete(simulacion)
        db.session.commit()

        flash("Simulación eliminada correctamente.", "success")

        return redirect(url_for("independencia"))