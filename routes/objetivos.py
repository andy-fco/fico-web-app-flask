from flask import request, redirect, url_for, render_template, flash
from extensions import db
from models.objetivo_ahorro import ObjetivoAhorro
from routes import login_required, get_usuario_actual
from datetime import date


def register_routes(app):

    @app.route("/dashboard/objetivos")
    @login_required
    def objetivos():
        usuario = get_usuario_actual()
        return render_template("dashboard/home.html", objetivos=usuario.objetivos)

    @app.route("/dashboard/objetivos/nuevo", methods=["POST"])
    @login_required
    def nuevo_objetivo():
        usuario        = get_usuario_actual()
        nombre         = request.form.get("nombre", "").strip()
        monto_objetivo = request.form.get("monto_objetivo", type=float)
        if not nombre or not monto_objetivo or monto_objetivo <= 0:
            flash("Nombre y monto objetivo son obligatorios.", "error")
            return redirect(url_for("dashboard"))
        try:
            f_limite = date.fromisoformat(request.form.get("fecha_limite")) if request.form.get("fecha_limite") else None
        except ValueError:
            f_limite = None
        db.session.add(ObjetivoAhorro(
            id_usuario=usuario.id_usuario, nombre=nombre,
            monto_objetivo=monto_objetivo, fecha_limite=f_limite,
        ))
        db.session.commit()
        flash("Objetivo creado.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/dashboard/objetivos/<int:id>/aportar", methods=["POST"])
    @login_required
    def aportar_objetivo(id):
        usuario  = get_usuario_actual()
        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        monto = request.form.get("monto", type=float)
        if not monto or monto <= 0:
            flash("El monto debe ser mayor a 0.", "error")
            return redirect(url_for("dashboard"))
        objetivo.aportar_monto(monto)
        db.session.commit()
        flash(f"Aporte de ${monto:,.0f} registrado.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/dashboard/objetivos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_objetivo(id):
        usuario  = get_usuario_actual()
        objetivo = ObjetivoAhorro.query.filter_by(
            id_objetivo=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        db.session.delete(objetivo)
        db.session.commit()
        flash("Objetivo eliminado.", "success")
        return redirect(url_for("dashboard"))
