from flask import request, redirect, url_for, render_template, flash, jsonify
from extensions import db
from models.transaccion import Transaccion
from models.presupuesto import Presupuesto
from controllers import login_required, get_usuario_actual
from datetime import date
from services.app_config import AppConfig


def register_routes(app):

    @app.route("/dashboard/movimientos")
    @login_required
    def movimientos():
        usuario = get_usuario_actual()
        config = AppConfig()

        transacciones = Transaccion.query.filter_by(
            id_usuario=usuario.id_usuario
        ).order_by(Transaccion.fecha.desc()).all()
        
        presupuestos = Presupuesto.query.filter_by(
            id_usuario=usuario.id_usuario
        ).order_by(Presupuesto.id_presupuesto.desc()).all()

        categorias_usuario = [
            c[0] for c in db.session.query(Transaccion.categoria)
            .filter_by(id_usuario=usuario.id_usuario)
            .distinct()
            .all()
        ]

        categorias = sorted(set(config.categorias_default + categorias_usuario))

        return render_template(
            "dashboard/movimientos.html",
            transacciones=transacciones,
            categorias=categorias,
            presupuestos=presupuestos
        )

    @app.route("/dashboard/movimientos/nueva", methods=["POST"])
    @login_required
    def nueva_transaccion():
        usuario = get_usuario_actual()

        tipo = request.form.get("tipo")
        monto = request.form.get("monto", type=float)
        moneda = request.form.get("moneda", "ARS")

        categoria_select = request.form.get("categoria_select", "").strip()
        categoria_nueva = request.form.get("categoria_nueva", "").strip()
        categoria = categoria_nueva if categoria_select == "__nueva__" else categoria_select

        descripcion = request.form.get("descripcion", "").strip()
        es_recurrente = request.form.get("es_recurrente") == "on"

        try:
            fecha = date.fromisoformat(request.form.get("fecha")) if request.form.get("fecha") else date.today()
        except ValueError:
            fecha = date.today()

        if tipo not in ["ingreso", "egreso"]:
            flash("El tipo de movimiento no es válido.", "error")
            return redirect(url_for("movimientos"))

        if not monto or monto <= 0:
            flash("El monto debe ser mayor a cero.", "error")
            return redirect(url_for("movimientos"))

        if moneda not in ["ARS", "USD"]:
            flash("La moneda no es válida.", "error")
            return redirect(url_for("movimientos"))

        if not categoria:
            flash("La categoría es obligatoria.", "error")
            return redirect(url_for("movimientos"))

        transaccion = Transaccion(
            id_usuario=usuario.id_usuario,
            tipo=tipo,
            monto=monto,
            moneda=moneda,
            categoria=categoria,
            fecha=fecha,
            descripcion=descripcion,
            es_recurrente=es_recurrente,
        )

        db.session.add(transaccion)
        db.session.commit()

        flash("Movimiento registrado correctamente.", "success")
        return redirect(url_for("movimientos"))

    @app.route("/dashboard/movimientos/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    def editar_transaccion(id):
        usuario = get_usuario_actual()
        config = AppConfig()

        transaccion = Transaccion.query.filter_by(
            id_transaccion=id,
            id_usuario=usuario.id_usuario
        ).first_or_404()
        
        presupuestos = Presupuesto.query.filter_by(
            id_usuario=usuario.id_usuario
        ).order_by(Presupuesto.id_presupuesto.desc()).all()

        categorias_usuario = [
            c[0] for c in db.session.query(Transaccion.categoria)
            .filter_by(id_usuario=usuario.id_usuario)
            .distinct()
            .all()
        ]

        categorias = sorted(set(config.categorias_default + categorias_usuario))

        if request.method == "POST":
            tipo = request.form.get("tipo")
            monto = request.form.get("monto", type=float)
            moneda = request.form.get("moneda", "ARS")

            categoria_select = request.form.get("categoria_select", "").strip()
            categoria_nueva = request.form.get("categoria_nueva", "").strip()
            categoria = categoria_nueva if categoria_select == "__nueva__" else categoria_select

            descripcion = request.form.get("descripcion", "").strip()
            es_recurrente = request.form.get("es_recurrente") == "on"

            try:
                fecha = date.fromisoformat(request.form.get("fecha")) if request.form.get("fecha") else transaccion.fecha
            except ValueError:
                fecha = transaccion.fecha

            if tipo not in ["ingreso", "egreso"]:
                flash("El tipo de movimiento no es válido.", "error")
                return redirect(url_for("editar_transaccion", id=id))

            if not monto or monto <= 0:
                flash("El monto debe ser mayor a cero.", "error")
                return redirect(url_for("editar_transaccion", id=id))

            if moneda not in ["ARS", "USD"]:
                flash("La moneda no es válida.", "error")
                return redirect(url_for("editar_transaccion", id=id))

            if not categoria:
                flash("La categoría es obligatoria.", "error")
                return redirect(url_for("editar_transaccion", id=id))

            transaccion.tipo = tipo
            transaccion.monto = monto
            transaccion.moneda = moneda
            transaccion.categoria = categoria
            transaccion.fecha = fecha
            transaccion.descripcion = descripcion
            transaccion.es_recurrente = es_recurrente

            db.session.commit()

            flash("Transacción actualizada correctamente.", "success")
            return redirect(url_for("movimientos"))
        
        transacciones = Transaccion.query.filter_by(
            id_usuario=usuario.id_usuario
        ).order_by(Transaccion.fecha.desc()).all()

        return render_template(
            "dashboard/movimientos.html",
            transaccion=transaccion,
            transacciones=transacciones,
            categorias=categorias,
            presupuestos=presupuestos
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