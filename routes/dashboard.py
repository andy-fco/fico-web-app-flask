from flask import render_template
from models.transaccion import Transaccion
from routes import login_required, get_usuario_actual
from datetime import date


def register_routes(app):

    @app.route("/dashboard")
    @login_required
    def dashboard():
        usuario = get_usuario_actual()
        hoy = date.today()

        transacciones_mes = Transaccion.query.filter(
            Transaccion.id_usuario == usuario.id_usuario,
            Transaccion.fecha >= date(hoy.year, hoy.month, 1),
            Transaccion.fecha <= hoy,
        ).order_by(Transaccion.fecha.desc()).all()

        ingresos_mes = sum(t.monto for t in transacciones_mes if t.tipo == "ingreso")
        egresos_mes = sum(t.monto for t in transacciones_mes if t.tipo == "egreso")

        objetivos = usuario.objetivos

        return render_template(
            "dashboard/home.html",
            usuario=usuario,
            ingresos_mes=ingresos_mes,
            egresos_mes=egresos_mes,
            ahorro_mes=ingresos_mes - egresos_mes,
            saldo_total=usuario.get_saldo_total(),
            ultimas_transacciones=transacciones_mes[:5],
            alertas=[],
            objetivos=objetivos,
        )