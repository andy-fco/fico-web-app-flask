from flask import Blueprint, request, redirect, url_for, render_template, flash
from app import db
from app.models.objetivo_ahorro import ObjetivoAhorro
from app.routes import login_required, get_usuario_actual
from datetime import date

objetivos_bp = Blueprint("objetivos", __name__, url_prefix="/objetivos")


@objetivos_bp.route("/")
@login_required
def index():
    usuario  = get_usuario_actual()
    objetivos = ObjetivoAhorro.query.filter_by(id_usuario=usuario.id_usuario).all()
    return render_template("objetivos/index.html", objetivos=objetivos)


@objetivos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    usuario = get_usuario_actual()

    if request.method == "POST":
        nombre         = request.form.get("nombre", "").strip()
        monto_objetivo = request.form.get("monto_objetivo", type=float)
        fecha_limite   = request.form.get("fecha_limite") or None

        if not nombre or not monto_objetivo or monto_objetivo <= 0:
            flash("Nombre y monto objetivo son obligatorios.", "error")
            return redirect(url_for("objetivos.nuevo"))

        try:
            f_limite = date.fromisoformat(fecha_limite) if fecha_limite else None
        except ValueError:
            f_limite = None

        objetivo = ObjetivoAhorro(
            id_usuario     = usuario.id_usuario,
            nombre         = nombre,
            monto_objetivo = monto_objetivo,
            fecha_limite   = f_limite,
        )
        db.session.add(objetivo)
        db.session.commit()
        flash("Objetivo creado.", "success")
        return redirect(url_for("objetivos.index"))

    return render_template("objetivos/nuevo.html")


@objetivos_bp.route("/<int:id>/aportar", methods=["POST"])
@login_required
def aportar(id):
    usuario = get_usuario_actual()
    objetivo = ObjetivoAhorro.query.filter_by(
        id_objetivo=id, id_usuario=usuario.id_usuario
    ).first_or_404()

    monto = request.form.get("monto", type=float)
    if not monto or monto <= 0:
        flash("El monto debe ser mayor a 0.", "error")
        return redirect(url_for("objetivos.index"))

    objetivo.aportar_monto(monto)
    db.session.commit()
    flash(f"Aporte de ${monto:,.0f} registrado.", "success")
    return redirect(url_for("objetivos.index"))


@objetivos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    usuario  = get_usuario_actual()
    objetivo = ObjetivoAhorro.query.filter_by(
        id_objetivo=id, id_usuario=usuario.id_usuario
    ).first_or_404()
    db.session.delete(objetivo)
    db.session.commit()
    flash("Objetivo eliminado.", "success")
    return redirect(url_for("objetivos.index"))
