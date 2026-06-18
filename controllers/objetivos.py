from flask import request, redirect, url_for, render_template, flash
from extensions import db
from models.objetivo_ahorro import ObjetivoAhorro
from controllers import login_required, get_usuario_actual
from datetime import date


def calcular_metricas_objetivos(objetivos):
    total_objetivos = len(objetivos)

    objetivos_activos = [
        objetivo for objetivo in objetivos
        if objetivo.estado == "activo"
    ]

    objetivos_logrados = [
        objetivo for objetivo in objetivos
        if objetivo.estado == "logrado"
    ]

    monto_ahorrado_ars = sum(
        float(objetivo.monto_actual)
        for objetivo in objetivos
        if objetivo.moneda == "ARS"
    )

    monto_ahorrado_usd = sum(
        float(objetivo.monto_actual)
        for objetivo in objetivos
        if objetivo.moneda == "USD"
    )

    progreso_promedio = 0

    if total_objetivos > 0:
        progreso_promedio = round(
            sum(objetivo.get_progreso() for objetivo in objetivos) / total_objetivos,
            2
        )

    return {
        "total": total_objetivos,
        "activos": len(objetivos_activos),
        "logrados": len(objetivos_logrados),
        "monto_ahorrado_ars": monto_ahorrado_ars,
        "monto_ahorrado_usd": monto_ahorrado_usd,
        "progreso_promedio": progreso_promedio,
    }


def register_routes(app):

    @app.route("/dashboard/objetivos")
    @login_required
    def objetivos():
        usuario = get_usuario_actual()
        objetivos_usuario = usuario.objetivos
        metricas = calcular_metricas_objetivos(objetivos_usuario)

        return render_template(
            "dashboard/objetivos.html",
            objetivos=objetivos_usuario,
            metricas=metricas
        )

    @app.route("/dashboard/objetivos/nuevo", methods=["POST"])
    @login_required
    def nuevo_objetivo():
        usuario = get_usuario_actual()

        nombre = request.form.get("nombre", "").strip()
        moneda = request.form.get("moneda", "ARS")
        monto_objetivo = request.form.get("monto_objetivo", type=float)
        monto_actual = request.form.get("monto_actual", type=float, default=0)

        if not nombre or not monto_objetivo or monto_objetivo <= 0:
            flash("Nombre y monto objetivo son obligatorios.", "error")
            return redirect(url_for("objetivos"))

        if monto_actual < 0:
            flash("El monto actual no puede ser negativo.", "error")
            return redirect(url_for("objetivos"))

        if monto_actual > monto_objetivo:
            flash("El monto actual no puede superar el monto objetivo.", "error")
            return redirect(url_for("objetivos"))

        try:
            fecha_limite = request.form.get("fecha_limite")
            f_limite = date.fromisoformat(fecha_limite) if fecha_limite else None
        except ValueError:
            flash("La fecha límite no tiene un formato válido.", "error")
            return redirect(url_for("objetivos"))

        objetivo = ObjetivoAhorro(
            id_usuario=usuario.id_usuario,
            nombre=nombre,
            moneda=moneda,
            monto_objetivo=monto_objetivo,
            monto_actual=monto_actual,
            fecha_limite=f_limite,
        )

        if objetivo.esta_completada():
            objetivo.estado = "logrado"

        db.session.add(objetivo)
        db.session.commit()

        flash("Objetivo creado correctamente.", "success")
        return redirect(url_for("objetivos"))

    @app.route("/dashboard/objetivos/<int:id>/aportar", methods=["POST"])
    @login_required
    def aportar_objetivo(id):
        usuario = get_usuario_actual()

        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        monto = request.form.get("monto", type=float)

        if not monto or monto <= 0:
            flash("El monto debe ser mayor a 0.", "error")
            return redirect(url_for("objetivos"))

        objetivo.aportar_monto(monto)
        db.session.commit()

        simbolo = "US$" if objetivo.moneda == "USD" else "$"

        flash(f"Aporte de {simbolo}{monto:,.0f} registrado.", "success")
        return redirect(url_for("objetivos"))
    
    @app.route("/dashboard/objetivos/<int:id>/pausar", methods=["POST"])
    @login_required
    def pausar_objetivo(id):
        usuario = get_usuario_actual()

        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        if objetivo.estado == "logrado":
            flash("No podés pausar un objetivo ya logrado.", "error")
            return redirect(url_for("objetivos"))

        objetivo.estado = "pausado"
        db.session.commit()

        flash("Objetivo pausado correctamente.", "success")
        return redirect(url_for("objetivos"))


    @app.route("/dashboard/objetivos/<int:id>/reactivar", methods=["POST"])
    @login_required
    def reactivar_objetivo(id):
        usuario = get_usuario_actual()

        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        if objetivo.esta_completada():
            objetivo.estado = "logrado"
        else:
            objetivo.estado = "activo"

        db.session.commit()

        flash("Objetivo reactivado correctamente.", "success")
        return redirect(url_for("objetivos"))

    @app.route("/dashboard/objetivos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_objetivo(id):
        usuario = get_usuario_actual()

        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        db.session.delete(objetivo)
        db.session.commit()

        flash("Objetivo eliminado correctamente.", "success")
        return redirect(url_for("objetivos"))