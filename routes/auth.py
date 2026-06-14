from flask import request, session, redirect, url_for, render_template, flash
from extensions import db
from models.usuario import Usuario


def register_routes(app):

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            usuario  = Usuario.query.filter_by(email=email).first()
            if not usuario or not usuario.check_password(password):
                flash("Email o contraseña incorrectos.", "error")
                return render_template("auth/login.html")
            session["id_usuario"] = usuario.id_usuario
            session.permanent = True
            return redirect(url_for("dashboard"))
        return render_template("auth/login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            nombre   = request.form.get("nombre", "").strip()
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not nombre or not email or not password:
                flash("Todos los campos son obligatorios.", "error")
                return render_template("auth/register.html")
            if password != confirm_password:
                flash("Las contraseñas no coinciden.", "error")
                return render_template("auth/register.html")
            if Usuario.query.filter_by(email=email).first():
                flash("Ya existe una cuenta con ese email.", "error")
                return render_template("auth/register.html")
            usuario = Usuario(nombre=nombre, email=email)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            session["id_usuario"] = usuario.id_usuario
            return redirect(url_for("dashboard"))
        return render_template("auth/register.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("Sesión cerrada correctamente.", "success")
        return redirect(url_for("login"))
