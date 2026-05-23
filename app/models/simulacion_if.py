from app import db
from datetime import date
import math


class SimulacionIF(db.Model):
    __tablename__ = "simulacion_if"

    id_simulacion      = db.Column(db.Integer, primary_key=True)
    id_usuario         = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    gastos_mensuales   = db.Column(db.Float, nullable=False)
    ahorro_disponible  = db.Column(db.Float, nullable=False, default=0.0)
    tasa_inversion     = db.Column(db.Float, nullable=False)
    edad_actual        = db.Column(db.Integer, nullable=False)
    edad_objetivo      = db.Column(db.Integer, nullable=False)
    capital_inicial    = db.Column(db.Float, nullable=False, default=0.0)
    capital_objetivo   = db.Column(db.Float, nullable=True)
    fecha_simulacion   = db.Column(db.Date, nullable=False, default=date.today)

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="simulaciones")

    def calcular_capital_objetivo(self) -> float:
        """Regla del 4%: capital necesario = gastos anuales / tasa de retiro."""
        tasa_retiro = self.tasa_inversion / 100
        if tasa_retiro == 0:
            return 0.0
        gastos_anuales = self.gastos_mensuales * 12
        return round(gastos_anuales / tasa_retiro, 2)

    def calcular_inversion_mensual(self) -> float:
        """Cuánto hay que aportar por mes para llegar al capital objetivo."""
        objetivo = self.capital_objetivo or self.calcular_capital_objetivo()
        meses    = (self.edad_objetivo - self.edad_actual) * 12
        if meses <= 0:
            return 0.0
        tasa_mensual = self.tasa_inversion / 12 / 100
        if tasa_mensual == 0:
            return round((objetivo - self.capital_inicial) / meses, 2)
        factor = ((1 + tasa_mensual) ** meses - 1) / tasa_mensual
        capital_crecido = self.capital_inicial * (1 + tasa_mensual) ** meses
        return round((objetivo - capital_crecido) / factor, 2)

    def calcular_tiempo(self) -> int:
        """Meses necesarios para alcanzar el capital objetivo."""
        objetivo     = self.capital_objetivo or self.calcular_capital_objetivo()
        tasa_mensual = self.tasa_inversion / 12 / 100
        if tasa_mensual == 0 and self.ahorro_disponible > 0:
            return math.ceil((objetivo - self.capital_inicial) / self.ahorro_disponible)
        if tasa_mensual == 0:
            return 0
        meses = 0
        capital = self.capital_inicial
        while capital < objetivo and meses < 1200:
            capital = capital * (1 + tasa_mensual) + self.ahorro_disponible
            meses += 1
        return meses

    def __repr__(self) -> str:
        return f"<SimulacionIF usuario={self.id_usuario} fecha={self.fecha_simulacion}>"
