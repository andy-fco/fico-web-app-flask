from flask import request, session, redirect, url_for, render_template, flash
from extensions import db
from models.usuario import Usuario
from models.categoria import Categoria


CATEGORIAS_DEFAULT = [
    {"nombre": "Vivienda",       "tipo": "egreso",  "color": "#3b82f6"},
    {"nombre": "Alimentación",   "tipo": "egreso",  "color": "#8b5cf6"},
    {"nombre": "Transporte",     "tipo": "egreso",  "color": "#f59e0b"},
    {"nombre": "Salud",          "tipo": "egreso",  "color": "#ef4444"},
    {"nombre": "Educación",      "tipo": "egreso",  "color": "#06b6d4"},
    {"nombre": "Ocio",           "tipo": "egreso",  "color": "#ec4899"},
    {"nombre": "Ropa",           "tipo": "egreso",  "color": "#a78bfa"},
    {"nombre": "Otros gastos",   "tipo": "egreso",  "color": "#52525b"},
    {"nombre": "Sueldo",         "tipo": "ingreso", "color": "#2cd195"},
    {"nombre": "Freelance",      "tipo": "ingreso", "color": "#22c55e"},
    {"nombre": "Otros ingresos", "tipo": "ingreso", "color": "#6ee7b7"},
]


def crear_categorias_default(id_usuario):
    for cat in CATEGORIAS_DEFAULT:
        db.session.add(Categoria(
            id_usuario=id_usuario,
            nombre=cat["nombre"],
            tipo=cat["tipo"],
            color=cat["color"],
            es_predeterminada=True,
        ))
    db.session.commit()


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
            if not nombre or not email or not password:
                flash("Todos los campos son obligatorios.", "error")
                return render_template("auth/register.html")
            if Usuario.query.filter_by(email=email).first():
                flash("Ya existe una cuenta con ese email.", "error")
                return render_template("auth/register.html")
            usuario = Usuario(nombre=nombre, email=email)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            crear_categorias_default(usuario.id_usuario)
            session["id_usuario"] = usuario.id_usuario
            return redirect(url_for("dashboard"))
        return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
