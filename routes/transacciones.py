from flask import request, redirect, url_for, render_template, flash, jsonify
from extensions import db
from models.transaccion import Transaccion
from routes import login_required, get_usuario_actual
from datetime import date


def register_routes(app):

    @app.route("/dashboard/movimientos")
    @login_required
    def movimientos():
        usuario = get_usuario_actual()

        transacciones = Transaccion.query.filter_by(
            id_usuario=usuario.id_usuario
        ).order_by(Transaccion.fecha.desc()).all()

        return render_template(
            "dashboard/movimientos.html",
            transacciones=transacciones
        )

    @app.route("/dashboard/movimientos/nueva", methods=["POST"])
    @login_required
    def nueva_transaccion():
        usuario = get_usuario_actual()

        tipo = request.form.get("tipo")
        monto = request.form.get("monto", type=float)
        categoria = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        es_recurrente = request.form.get("es_recurrente") == "on"

        try:
            fecha = date.fromisoformat(request.form.get("fecha")) if request.form.get("fecha") else date.today()
        except ValueError:
            fecha = date.today()

        if not tipo or not monto or monto <= 0 or not categoria:
            flash("Tipo, monto y categoría son obligatorios.", "error")
            return redirect(url_for("movimientos"))

        db.session.add(Transaccion(
            id_usuario=usuario.id_usuario,
            tipo=tipo,
            monto=monto,
            categoria=categoria,
            fecha=fecha,
            descripcion=descripcion,
            es_recurrente=es_recurrente,
        ))

        db.session.commit()

        flash("Transacción registrada.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/dashboard/movimientos/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    def editar_transaccion(id):
        usuario = get_usuario_actual()

        transaccion = Transaccion.query.filter_by(
            id_transaccion=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        if request.method == "POST":
            tipo = request.form.get("tipo")
            monto = request.form.get("monto", type=float)
            categoria = request.form.get("categoria", "").strip()

            if not tipo or not monto or monto <= 0 or not categoria:
                flash("Tipo, monto y categoría son obligatorios.", "error")
                return redirect(url_for("movimientos"))

            transaccion.tipo = tipo
            transaccion.monto = monto
            transaccion.categoria = categoria
            transaccion.descripcion = request.form.get("descripcion", "").strip()
            transaccion.es_recurrente = request.form.get("es_recurrente") == "on"

            try:
                if request.form.get("fecha"):
                    transaccion.fecha = date.fromisoformat(request.form.get("fecha"))
            except ValueError:
                pass

            db.session.commit()

            flash("Transacción actualizada.", "success")
            return redirect(url_for("movimientos"))

        return render_template(
            "dashboard/movimientos.html",
            transaccion=transaccion
        )

    @app.route("/dashboard/movimientos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_transaccion(id):
        usuario = get_usuario_actual()

        transaccion = Transaccion.query.filter_by(
            id_transaccion=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()

        db.session.delete(transaccion)
        db.session.commit()

        flash("Transacción eliminada.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/api/transacciones")
    @login_required
    def api_transacciones():
        usuario = get_usuario_actual()

        transacciones = Transaccion.query.filter_by(
            id_usuario=usuario.id_usuario
        ).all()

        return jsonify([t.to_dict() for t in transacciones])