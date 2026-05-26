from flask import request, redirect, url_for, render_template, flash
from extensions import db
from models.presupuesto import Presupuesto
from models.categoria import Categoria
from routes import login_required, get_usuario_actual
from datetime import date


def register_routes(app):

    @app.route("/dashboard/presupuestos")
    @login_required
    def presupuestos():
        usuario = get_usuario_actual()
        return render_template("dashboard/home.html",
                               presupuestos=Presupuesto.query.filter_by(id_usuario=usuario.id_usuario).all())

    @app.route("/dashboard/presupuestos/nuevo", methods=["POST"])
    @login_required
    def nuevo_presupuesto():
        usuario      = get_usuario_actual()
        id_categoria = request.form.get("id_categoria", type=int)
        limite_gasto = request.form.get("limite_gasto", type=float)
        periodo      = request.form.get("periodo")
        if not id_categoria or not limite_gasto or not periodo:
            flash("Categoria, limite y periodo son obligatorios.", "error")
            return redirect(url_for("presupuestos"))
        try:
            f_inicio = date.fromisoformat(request.form.get("fecha_inicio")) if request.form.get("fecha_inicio") else date.today()
            f_fin    = date.fromisoformat(request.form.get("fecha_fin")) if request.form.get("fecha_fin") else None
        except ValueError:
            f_inicio = date.today()
            f_fin    = None
        db.session.add(Presupuesto(
            id_usuario=usuario.id_usuario, id_categoria=id_categoria,
            limite_gasto=limite_gasto, periodo=periodo,
            fecha_inicio=f_inicio, fecha_fin=f_fin,
        ))
        db.session.commit()
        flash("Presupuesto creado.", "success")
        return redirect(url_for("presupuestos"))

    @app.route("/dashboard/presupuestos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_presupuesto(id):
        usuario     = get_usuario_actual()
        presupuesto = Presupuesto.query.filter_by(
            id_presupuesto=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        db.session.delete(presupuesto)
        db.session.commit()
        flash("Presupuesto eliminado.", "success")
        return redirect(url_for("presupuestos"))
