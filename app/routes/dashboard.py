from flask import Blueprint, render_template
from app.routes import login_required, get_usuario_actual
from app.models.transaccion import Transaccion
from app.models.alerta import Alerta
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    usuario = get_usuario_actual()
    hoy     = date.today()

    # Transacciones del mes actual
    transacciones_mes = Transaccion.query.filter(
        Transaccion.id_usuario == usuario.id_usuario,
        Transaccion.fecha >= date(hoy.year, hoy.month, 1),
        Transaccion.fecha <= hoy,
    ).order_by(Transaccion.fecha.desc()).all()

    ingresos_mes = sum(t.monto for t in transacciones_mes if t.tipo == "ingreso")
    egresos_mes  = sum(t.monto for t in transacciones_mes if t.tipo == "egreso")
    ahorro_mes   = ingresos_mes - egresos_mes

    # Últimas 5 transacciones
    ultimas_transacciones = transacciones_mes[:5]

    # Alertas no leídas
    alertas = Alerta.query.filter_by(
        id_usuario=usuario.id_usuario,
        leida=False
    ).order_by(Alerta.fecha.desc()).all()

    # Objetivos activos
    objetivos = usuario.objetivos

    return render_template(
        "dashboard/index.html",
        usuario=usuario,
        ingresos_mes=ingresos_mes,
        egresos_mes=egresos_mes,
        ahorro_mes=ahorro_mes,
        saldo_total=usuario.get_saldo_total(),
        ultimas_transacciones=ultimas_transacciones,
        alertas=alertas,
        objetivos=objetivos,
    )
