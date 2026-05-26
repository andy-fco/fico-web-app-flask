from flask import request, redirect, url_for, render_template, flash
from extensions import db
from models.categoria import Categoria
from routes import login_required, get_usuario_actual


def register_routes(app):

    @app.route("/dashboard/categorias")
    @login_required
    def categorias():
        usuario = get_usuario_actual()
        return render_template("dashboard/categorias.html",
                               categorias=Categoria.query.filter_by(id_usuario=usuario.id_usuario).all())

    @app.route("/dashboard/categorias/nueva", methods=["POST"])
    @login_required
    def nueva_categoria():
        usuario = get_usuario_actual()
        nombre  = request.form.get("nombre", "").strip()
        tipo    = request.form.get("tipo")
        color   = request.form.get("color", "#2cd195")
        if not nombre or not tipo:
            flash("Nombre y tipo son obligatorios.", "error")
            return redirect(url_for("categorias"))
        db.session.add(Categoria(id_usuario=usuario.id_usuario, nombre=nombre, tipo=tipo, color=color))
        db.session.commit()
        flash("Categoria creada.", "success")
        return redirect(url_for("categorias"))

    @app.route("/dashboard/categorias/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    def editar_categoria(id):
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
            return redirect(url_for("categorias"))
        return render_template("dashboard/categorias.html", categoria=categoria,
                               categorias=Categoria.query.filter_by(id_usuario=usuario.id_usuario).all())

    @app.route("/dashboard/categorias/<int:id>/eliminar", methods=["POST"])
    @login_required
    def eliminar_categoria(id):
        usuario   = get_usuario_actual()
        categoria = Categoria.query.filter_by(
            id_categoria=id, id_usuario=usuario.id_usuario
        ).first_or_404()
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoria eliminada.", "success")
        return redirect(url_for("categorias"))
