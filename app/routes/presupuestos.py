from flask import Blueprint, request, redirect, url_for, render_template, flash
from app import db
from app.models.presupuesto import Presupuesto
from app.models.categoria import Categoria
from app.routes import login_required, get_usuario_actual
from datetime import date

presupuestos_bp = Blueprint("presupuestos", __name__, url_prefix="/presupuestos")


@presupuestos_bp.route("/")
@login_required
def index():
    usuario      = get_usuario_actual()
    presupuestos = Presupuesto.query.filter_by(id_usuario=usuario.id_usuario).all()
    return render_template("presupuestos/index.html", presupuestos=presupuestos)


@presupuestos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    usuario = get_usuario_actual()

    if request.method == "POST":
        id_categoria  = request.form.get("id_categoria", type=int)
        limite_gasto  = request.form.get("limite_gasto", type=float)
        periodo       = request.form.get("periodo")
        fecha_inicio  = request.form.get("fecha_inicio")
        fecha_fin     = request.form.get("fecha_fin") or None

        if not id_categoria or not limite_gasto or not periodo:
            flash("Categoria, limite y periodo son obligatorios.", "error")
            return redirect(url_for("presupuestos.nuevo"))

        try:
            f_inicio = date.fromisoformat(fecha_inicio) if fecha_inicio else date.today()
            f_fin    = date.fromisoformat(fecha_fin) if fecha_fin else None
        except ValueError:
            f_inicio = date.today()
            f_fin    = None

        presupuesto = Presupuesto(
            id_usuario   = usuario.id_usuario,
            id_categoria = id_categoria,
            limite_gasto = limite_gasto,
            periodo      = periodo,
            fecha_inicio = f_inicio,
            fecha_fin    = f_fin,
        )
        db.session.add(presupuesto)
        db.session.commit()
        flash("Presupuesto creado.", "success")
        return redirect(url_for("presupuestos.index"))

    categorias = Categoria.query.filter_by(
        id_usuario=usuario.id_usuario, tipo="egreso"
    ).all()
    return render_template("presupuestos/nuevo.html", categorias=categorias)


@presupuestos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    usuario     = get_usuario_actual()
    presupuesto = Presupuesto.query.filter_by(
        id_presupuesto=id, id_usuario=usuario.id_usuario
    ).first_or_404()
    db.session.delete(presupuesto)
    db.session.commit()
    flash("Presupuesto eliminado.", "success")
    return redirect(url_for("presupuestos.index"))
