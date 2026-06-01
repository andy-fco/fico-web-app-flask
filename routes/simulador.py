from flask import request, render_template, flash, redirect, url_for
from extensions import db
from models.simulacion_if import SimulacionIF
from routes import login_required, get_usuario_actual


def register_routes(app):

    @app.route("/dashboard/proyecciones")
    @login_required
    def proyecciones():
        return render_template("dashboard/proyecciones.html")


    @app.route("/dashboard/proyecciones/calcular", methods=["POST"])
    @login_required
    def calcular_proyeccion():
        flash("La sección de proyecciones todavía no tiene lógica activa.", "error")
        return redirect(url_for("proyecciones"))


    @app.route("/dashboard/independencia")
    @login_required
    def independencia():
        usuario = get_usuario_actual()

        return render_template(
            "dashboard/independencia.html",
            simulaciones=usuario.simulaciones
        )


    @app.route("/dashboard/independencia/calcular", methods=["POST"])
    @login_required
    def calcular_independencia():
        usuario = get_usuario_actual()

        simulacion = SimulacionIF(
            id_usuario=usuario.id_usuario,
            gastos_mensuales=request.form.get("gastos_mensuales", type=float, default=0),
            ahorro_disponible=request.form.get("ahorro_disponible", type=float, default=0),
            tasa_rendimiento=request.form.get("tasa_rendimiento", type=float, default=0),
            tasa_retiro=request.form.get("tasa_retiro", type=float, default=4.0),
            edad_actual=request.form.get("edad_actual", type=int, default=25),
            edad_objetivo=request.form.get("edad_objetivo", type=int, default=60),
            capital_inicial=request.form.get("capital_inicial", type=float, default=0),
            capital_objetivo=request.form.get("capital_objetivo", type=float) or None,
        )

        db.session.add(simulacion)
        db.session.commit()

        flash("Simulación guardada.", "success")

        return render_template(
            "dashboard/independencia.html",
            simulaciones=usuario.simulaciones,
            resultado=simulacion
        )