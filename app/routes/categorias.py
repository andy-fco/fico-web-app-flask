from flask import Blueprint, request, redirect, url_for, render_template, flash
from app import db
from app.models.categoria import Categoria
from app.routes import login_required, get_usuario_actual

categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias")


@categorias_bp.route("/")
@login_required
def index():
    usuario    = get_usuario_actual()
    categorias = Categoria.query.filter_by(id_usuario=usuario.id_usuario).all()
    return render_template("categorias/index.html", categorias=categorias)


@categorias_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    usuario = get_usuario_actual()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        tipo   = request.form.get("tipo")
        color  = request.form.get("color", "#2cd195")

        if not nombre or not tipo:
            flash("Nombre y tipo son obligatorios.", "error")
            return redirect(url_for("categorias.nueva"))

        categoria = Categoria(
            id_usuario=usuario.id_usuario,
            nombre=nombre,
            tipo=tipo,
            color=color,
        )
        db.session.add(categoria)
        db.session.commit()
        flash("Categoria creada.", "success")
        return redirect(url_for("categorias.index"))

    return render_template("categorias/nueva.html")


@categorias_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    usuario   = get_usuario_actual()
    categoria = Categoria.query.filter_by(
        id_categoria=id, id_usuario=usuario.id_usuario
    ).first_or_404()

    if request.method == "POST":
        categoria.nombre = request.form.get("nombre", "").strip()
        categoria.tipo   = request.form.get("tipo")
        categoria.color  = request.form.get("color", categoria.color)
        db.session.commit()
        flash("Categoria actualizada.", "success")
        return redirect(url_for("categorias.index"))

    return render_template("categorias/editar.html", categoria=categoria)


@categorias_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    usuario   = get_usuario_actual()
    categoria = Categoria.query.filter_by(
        id_categoria=id, id_usuario=usuario.id_usuario
    ).first_or_404()
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria eliminada.", "success")
    return redirect(url_for("categorias.index"))
