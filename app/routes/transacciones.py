from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify
from app import db
from app.models.transaccion import Transaccion
from app.models.categoria import Categoria
from app.routes import login_required, get_usuario_actual
from datetime import date

transacciones_bp = Blueprint("transacciones", __name__, url_prefix="/transacciones")


@transacciones_bp.route("/")
@login_required
def index():
    usuario = get_usuario_actual()
    transacciones = Transaccion.query.filter_by(
        id_usuario=usuario.id_usuario
    ).order_by(Transaccion.fecha.desc()).all()
    return render_template("transacciones/index.html", transacciones=transacciones)


@transacciones_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    usuario = get_usuario_actual()

    if request.method == "POST":
        tipo          = request.form.get("tipo")
        monto         = request.form.get("monto", type=float)
        fecha_str     = request.form.get("fecha")
        descripcion   = request.form.get("descripcion", "").strip()
        id_categoria  = request.form.get("id_categoria", type=int)
        es_recurrente = request.form.get("es_recurrente") == "on"
        fuente        = request.form.get("fuente", "").strip() or None
        tipo_gasto    = request.form.get("tipo_gasto", "").strip() or None

        if not tipo or not monto or monto <= 0:
            flash("Tipo y monto son obligatorios y el monto debe ser mayor a 0.", "error")
            return redirect(url_for("transacciones.nueva"))

        try:
            fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
        except ValueError:
            fecha = date.today()

        transaccion = Transaccion(
            id_usuario    = usuario.id_usuario,
            id_categoria  = id_categoria,
            tipo          = tipo,
            monto         = monto,
            fecha         = fecha,
            descripcion   = descripcion,
            es_recurrente = es_recurrente,
            fuente        = fuente,
            tipo_gasto    = tipo_gasto,
        )
        db.session.add(transaccion)
        db.session.commit()
        flash("Transaccion registrada correctamente.", "success")
        return redirect(url_for("transacciones.index"))

    categorias = Categoria.query.filter_by(id_usuario=usuario.id_usuario).all()
    return render_template("transacciones/nueva.html", categorias=categorias)


@transacciones_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
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

        fecha_str = request.form.get("fecha")
        try:
            transaccion.fecha = date.fromisoformat(fecha_str) if fecha_str else transaccion.fecha
        except ValueError:
            pass

        db.session.commit()
        flash("Transaccion actualizada.", "success")
        return redirect(url_for("transacciones.index"))

    categorias = Categoria.query.filter_by(id_usuario=usuario.id_usuario).all()
    return render_template("transacciones/editar.html", transaccion=transaccion, categorias=categorias)


@transacciones_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    usuario     = get_usuario_actual()
    transaccion = Transaccion.query.filter_by(
        id_transaccion=id, id_usuario=usuario.id_usuario
    ).first_or_404()
    db.session.delete(transaccion)
    db.session.commit()
    flash("Transaccion eliminada.", "success")
    return redirect(url_for("transacciones.index"))


@transacciones_bp.route("/api/lista")
@login_required
def api_lista():
    """Endpoint JSON para Chart.js del dashboard."""
    usuario = get_usuario_actual()
    transacciones = Transaccion.query.filter_by(id_usuario=usuario.id_usuario).all()
    return jsonify([t.to_dict() for t in transacciones])
