from functools import wraps
from flask import session, redirect, url_for
from app.models.usuario import Usuario


def login_required(f):
    """Decorador que protege rutas que requieren sesión activa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "id_usuario" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_usuario_actual() -> Usuario | None:
    """Retorna el usuario de la sesión actual."""
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return None
    return Usuario.query.get(id_usuario)
