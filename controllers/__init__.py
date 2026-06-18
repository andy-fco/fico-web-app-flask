from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "id_usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def get_usuario_actual():
    from models.usuario import Usuario
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return None
    return Usuario.query.get(id_usuario)
