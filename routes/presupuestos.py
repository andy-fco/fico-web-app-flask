from flask import request, redirect, url_for, flash
from extensions import db
from models.presupuesto import Presupuesto
from routes import login_required, get_usuario_actual
from datetime import date


PERIODOS_VALIDOS = {"semana", "mes", "año"}
MONEDAS_VALIDAS = {"ARS", "USD"}


def register_routes(app):

    @app.route("/dashboard/presupuestos/nuevo", methods=["POST"])
    @login_required
    def nuevo_presupuesto():
        usuario = get_usuario_actual()

        categoria = (request.form.get("categoria") or "").strip()
        limite_gasto = request.form.get("limite_gasto", type=float)
        moneda = request.form.get("moneda") or "ARS"
        periodo = request.form.get("periodo") or "mes"

        if not categoria:
            flash("La categoría del presupuesto es obligatoria.", "error")
            return redirect(url_for("movimientos"))

        if not limite_gasto or limite_gasto <= 0:
            flash("El límite del presupuesto debe ser mayor a cero.", "error")
            return redirect(url_for("movimientos"))

        if moneda not in MONEDAS_VALIDAS:
            flash("La moneda seleccionada no es válida.", "error")
            return redirect(url_for("movimientos"))

        if periodo not in PERIODOS_VALIDOS:
            periodo = "mes"

        presupuesto = Presupuesto(
            id_usuario=usuario.id_usuario,
            categoria=categoria,
            limite_gasto=limite_gasto,
            moneda=moneda,
            periodo=periodo,
            fecha_inicio=date.today(),
            activo=True,
        )

        db.session.add(presupuesto)
        db.session.commit()

        flash("Presupuesto creado correctamente.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/dashboard/presupuestos/<int:id>/editar", methods=["POST"])
    @login_required
    def editar_presupuesto(id):
        usuario = get_usuario_actual()

        presupuesto = Presupuesto.query.filter_by(
            id_presupuesto=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        categoria = (request.form.get("categoria") or "").strip()
        limite_gasto = request.form.get("limite_gasto", type=float)
        moneda = request.form.get("moneda") or "ARS"
        periodo = request.form.get("periodo") or "mes"

        if not categoria:
            flash("La categoría del presupuesto es obligatoria.", "error")
            return redirect(url_for("movimientos"))

        if not limite_gasto or limite_gasto <= 0:
            flash("El límite del presupuesto debe ser mayor a cero.", "error")
            return redirect(url_for("movimientos"))

        if moneda not in MONEDAS_VALIDAS:
            flash("La moneda seleccionada no es válida.", "error")
            return redirect(url_for("movimientos"))

        if periodo not in PERIODOS_VALIDOS:
            periodo = "mes"

        presupuesto.categoria = categoria
        presupuesto.limite_gasto = limite_gasto
        presupuesto.moneda = moneda
        presupuesto.periodo = periodo

        db.session.commit()

        flash("Presupuesto actualizado correctamente.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/dashboard/presupuestos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_presupuesto(id):
        usuario = get_usuario_actual()

        presupuesto = Presupuesto.query.filter_by(
            id_presupuesto=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        db.session.delete(presupuesto)
        db.session.commit()

        flash("Presupuesto eliminado correctamente.", "success")
        return redirect(url_for("movimientos"))