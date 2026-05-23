from flask import Blueprint, request, render_template, jsonify
from app import db
from app.models.proyeccion import ProyeccionFinanciera
from app.models.simulacion_if import SimulacionIF
from app.routes import login_required, get_usuario_actual

simulador_bp = Blueprint("simulador", __name__, url_prefix="/simulador")


@simulador_bp.route("/")
@login_required
def index():
    usuario = get_usuario_actual()
    return render_template(
        "simulador/index.html",
        proyecciones=usuario.proyecciones,
        simulaciones=usuario.simulaciones,
    )


# ── Proyección financiera ──────────────────────────────────────────────────

@simulador_bp.route("/proyeccion", methods=["POST"])
@login_required
def calcular_proyeccion():
    usuario = get_usuario_actual()

    ahorro_mensual   = request.form.get("ahorro_mensual",   type=float, default=0)
    capital_inicial  = request.form.get("capital_inicial",  type=float, default=0)
    tasa_interes     = request.form.get("tasa_interes",     type=float, default=0)
    objetivo_capital = request.form.get("objetivo_capital", type=float) or None
    horizonte        = request.form.get("horizonte")

    proyeccion = ProyeccionFinanciera(
        id_usuario       = usuario.id_usuario,
        ahorro_mensual   = ahorro_mensual,
        capital_inicial  = capital_inicial,
        tasa_interes     = tasa_interes,
        objetivo_capital = objetivo_capital,
        horizonte        = horizonte,
    )

    # Pre-calcular y guardar resultado
    meses_map = {"1a": 12, "5a": 60, "10a": 120}
    meses = meses_map.get(horizonte, 12)
    proyeccion.capital_proyectado = proyeccion.calcular_capital_futuro(meses)

    db.session.add(proyeccion)
    db.session.commit()

    return render_template(
        "simulador/resultado_proyeccion.html",
        proyeccion=proyeccion,
        meses=meses,
        tiempo_objetivo=proyeccion.calcular_tiempo_objetivo(),
    )


@simulador_bp.route("/proyeccion/api", methods=["POST"])
@login_required
def api_proyeccion():
    """Endpoint JSON para cálculo en tiempo real desde el frontend."""
    data            = request.get_json()
    ahorro_mensual  = float(data.get("ahorro_mensual", 0))
    capital_inicial = float(data.get("capital_inicial", 0))
    tasa_interes    = float(data.get("tasa_interes", 0))

    p = ProyeccionFinanciera(
        ahorro_mensual=ahorro_mensual,
        capital_inicial=capital_inicial,
        tasa_interes=tasa_interes,
    )

    return jsonify({
        "1_anio":   p.calcular_capital_futuro(12),
        "5_anios":  p.calcular_capital_futuro(60),
        "10_anios": p.calcular_capital_futuro(120),
    })


# ── Simulación independencia financiera ───────────────────────────────────

@simulador_bp.route("/independencia", methods=["POST"])
@login_required
def calcular_if():
    usuario = get_usuario_actual()

    gastos_mensuales  = request.form.get("gastos_mensuales",  type=float, default=0)
    ahorro_disponible = request.form.get("ahorro_disponible", type=float, default=0)
    tasa_inversion    = request.form.get("tasa_inversion",    type=float, default=0)
    edad_actual       = request.form.get("edad_actual",       type=int,   default=25)
    edad_objetivo     = request.form.get("edad_objetivo",     type=int,   default=60)
    capital_inicial   = request.form.get("capital_inicial",   type=float, default=0)

    simulacion = SimulacionIF(
        id_usuario        = usuario.id_usuario,
        gastos_mensuales  = gastos_mensuales,
        ahorro_disponible = ahorro_disponible,
        tasa_inversion    = tasa_inversion,
        edad_actual       = edad_actual,
        edad_objetivo     = edad_objetivo,
        capital_inicial   = capital_inicial,
    )
    simulacion.capital_objetivo = simulacion.calcular_capital_objetivo()

    db.session.add(simulacion)
    db.session.commit()

    return render_template(
        "simulador/resultado_if.html",
        simulacion=simulacion,
        inversion_mensual=simulacion.calcular_inversion_mensual(),
        tiempo_meses=simulacion.calcular_tiempo(),
    )
