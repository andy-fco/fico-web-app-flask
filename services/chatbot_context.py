from datetime import date
from extensions import db
from models.transaccion import Transaccion
from models.presupuesto import Presupuesto
from models.objetivo_ahorro import ObjetivoAhorro
from models.simulacion_if import SimulacionIF


def build_chatbot_context(usuario_id: int) -> str:
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)

    ingresos_mes = db.session.query(db.func.sum(Transaccion.monto)).filter(
        Transaccion.id_usuario == usuario_id,
        Transaccion.tipo == "ingreso",
        Transaccion.fecha >= inicio_mes,
        Transaccion.fecha <= hoy,
    ).scalar() or 0

    egresos_mes = db.session.query(db.func.sum(Transaccion.monto)).filter(
        Transaccion.id_usuario == usuario_id,
        Transaccion.tipo == "egreso",
        Transaccion.fecha >= inicio_mes,
        Transaccion.fecha <= hoy,
    ).scalar() or 0

    ultimas_transacciones = (
        Transaccion.query
        .filter_by(id_usuario=usuario_id)
        .order_by(Transaccion.fecha.desc(), Transaccion.id_transaccion.desc())
        .limit(8)
        .all()
    )

    presupuestos = (
        Presupuesto.query
        .filter_by(id_usuario=usuario_id, activo=True)
        .limit(5)
        .all()
    )

    objetivos = (
        ObjetivoAhorro.query
        .filter_by(id_usuario=usuario_id)
        .order_by(ObjetivoAhorro.id_objetivo.desc())
        .limit(5)
        .all()
    )

    ultima_simulacion = (
        SimulacionIF.query
        .filter_by(id_usuario=usuario_id)
        .order_by(SimulacionIF.fecha_simulacion.desc(), SimulacionIF.id_simulacion.desc())
        .first()
    )

    lineas = [
        "Contexto financiero real del usuario:",
        f"- Fecha actual: {hoy.isoformat()}",
        f"- Ingresos del mes: {float(ingresos_mes):.2f}",
        f"- Egresos del mes: {float(egresos_mes):.2f}",
        f"- Balance del mes: {float(ingresos_mes) - float(egresos_mes):.2f}",
        "",
        "Últimas transacciones:",
    ]

    if ultimas_transacciones:
        for t in ultimas_transacciones:
            lineas.append(
                f"- {t.fecha}: {t.tipo} de {float(t.monto):.2f} {t.moneda} "
                f"en {t.categoria}. Descripción: {t.descripcion or 'sin descripción'}."
            )
    else:
        lineas.append("- No hay transacciones registradas.")

    lineas.append("")
    lineas.append("Presupuestos activos:")

    if presupuestos:
        for p in presupuestos:
            lineas.append(
                f"- {p.categoria}: límite {float(p.limite_gasto):.2f} {p.moneda}, "
                f"gastado {p.get_gasto_actual():.2f}, usado {p.get_porcentaje_usado():.2f}%."
            )
    else:
        lineas.append("- No hay presupuestos activos.")

    lineas.append("")
    lineas.append("Objetivos de ahorro:")

    if objetivos:
        for o in objetivos:
            lineas.append(
                f"- {o.nombre}: {float(o.monto_actual):.2f}/{float(o.monto_objetivo):.2f} "
                f"{o.moneda}, progreso {o.get_progreso():.2f}%, estado {o.estado}."
            )
    else:
        lineas.append("- No hay objetivos cargados.")

    lineas.append("")
    lineas.append("Última simulación de independencia financiera:")

    if ultima_simulacion:
        lineas.append(
            f"- Gastos mensuales: {float(ultima_simulacion.gastos_mensuales):.2f} "
            f"{ultima_simulacion.moneda}. Ahorro disponible: "
            f"{float(ultima_simulacion.ahorro_disponible):.2f}. "
            f"Capital objetivo: {float(ultima_simulacion.capital_objetivo or ultima_simulacion.calcular_capital_objetivo()):.2f}. "
            f"Edad actual: {ultima_simulacion.edad_actual}. "
            f"Edad objetivo: {ultima_simulacion.edad_objetivo}."
        )
    else:
        lineas.append("- No hay simulaciones guardadas.")

    return "\n".join(lineas)