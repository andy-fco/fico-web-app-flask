from flask import request, redirect, url_for, render_template, flash, jsonify
from extensions import db
from models.transaccion import Transaccion
from models.categoria import Categoria
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
        categorias = Categoria.query.filter_by(id_usuario=usuario.id_usuario).all()
        return render_template("dashboard/movimientos.html",
                               transacciones=transacciones, categorias=categorias)

    @app.route("/dashboard/movimientos/nueva", methods=["POST"])
    @login_required
    def nueva_transaccion():
        usuario       = get_usuario_actual()
        tipo          = request.form.get("tipo")
        monto         = request.form.get("monto", type=float)
        descripcion   = request.form.get("descripcion", "").strip()
        id_categoria  = request.form.get("id_categoria", type=int)
        es_recurrente = request.form.get("es_recurrente") == "on"
        fuente        = request.form.get("fuente", "").strip() or None
        tipo_gasto    = request.form.get("tipo_gasto", "").strip() or None
        try:
            fecha = date.fromisoformat(request.form.get("fecha")) if request.form.get("fecha") else date.today()
        except ValueError:
            fecha = date.today()
        if not tipo or not monto or monto <= 0:
            flash("Tipo y monto son obligatorios.", "error")
            return redirect(url_for("movimientos"))
        db.session.add(Transaccion(
            id_usuario=usuario.id_usuario, id_categoria=id_categoria,
            tipo=tipo, monto=monto, fecha=fecha, descripcion=descripcion,
            es_recurrente=es_recurrente, fuente=fuente, tipo_gasto=tipo_gasto,
        ))
        db.session.commit()
        flash("Transaccion registrada.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/dashboard/movimientos/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    def editar_transaccion(id):
        usuario     = get_usuario_actual()
        transaccion = Transaccion.query.filter_by(
            id_transaccion=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        if request.method == "POST":
            transaccion.tipo          = request.form.get("tipo")
            transaccion.monto         = request.form.get("monto", type=float)
            transaccion.descripcion   = request.form.get("descripcion", "").strip()
            transaccion.id_categoria  = request.form.get("id_categoria", type=int)
            transaccion.es_recurrente = request.form.get("es_recurrente") == "on"
            transaccion.fuente        = request.form.get("fuente", "").strip() or None
            transaccion.tipo_gasto    = request.form.get("tipo_gasto", "").strip() or None
            try:
                transaccion.fecha = date.fromisoformat(request.form.get("fecha")) if request.form.get("fecha") else transaccion.fecha
            except ValueError:
                pass
            db.session.commit()
            flash("Transaccion actualizada.", "success")
            return redirect(url_for("movimientos"))
        categorias = Categoria.query.filter_by(id_usuario=usuario.id_usuario).all()
        return render_template("dashboard/movimientos.html",
                               transaccion=transaccion, categorias=categorias)

    @app.route("/dashboard/movimientos/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_transaccion(id):
        usuario     = get_usuario_actual()
        transaccion = Transaccion.query.filter_by(
            id_transaccion=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        db.session.delete(transaccion)
        db.session.commit()
        flash("Transaccion eliminada.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/api/transacciones")
    @login_required
    def api_transacciones():
        usuario = get_usuario_actual()
        return jsonify([t.to_dict() for t in
                        Transaccion.query.filter_by(id_usuario=usuario.id_usuario).all()])
