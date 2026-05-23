from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre   = request.form.get("nombre", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("auth/registro.html")

        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese email.", "error")
            return render_template("auth/registro.html")

        usuario = Usuario(nombre=nombre, email=email)
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()

        session["id_usuario"] = usuario.id_usuario
        return redirect(url_for("dashboard.index"))

    return render_template("auth/registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not usuario.check_password(password):
            flash("Email o contraseña incorrectos.", "error")
            return render_template("auth/login.html")

        session["id_usuario"] = usuario.id_usuario
        session.permanent = True
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
