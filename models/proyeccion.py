from extensions import db
from datetime import date


class ProyeccionFinanciera(db.Model):
    __tablename__ = "proyeccion_financiera"

    id_proyeccion      = db.Column(db.Integer, primary_key=True)
    id_usuario         = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    ahorro_mensual     = db.Column(db.Float, nullable=False)
    capital_inicial    = db.Column(db.Float, nullable=False, default=0.0)
    tasa_interes       = db.Column(db.Float, nullable=False, default=0.0)
    objetivo_capital   = db.Column(db.Float, nullable=True)
    horizonte          = db.Column(db.Enum("1a", "5a", "10a", name="horizonte_proyeccion"), nullable=True)
    capital_proyectado = db.Column(db.Float, nullable=True)
    fecha_generacion   = db.Column(db.Date, nullable=False, default=date.today)

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="proyecciones")

    def calcular_capital_futuro(self, meses: int) -> float:
        """Fórmula de interés compuesto con aportes mensuales."""
        tasa_mensual = self.tasa_interes / 12 / 100
        if tasa_mensual == 0:
            return self.capital_inicial + self.ahorro_mensual * meses
        capital = self.capital_inicial * (1 + tasa_mensual) ** meses
        capital += self.ahorro_mensual * (((1 + tasa_mensual) ** meses - 1) / tasa_mensual)
        return round(capital, 2)

    def calcular_tiempo_objetivo(self) -> int | None:
        """Retorna los meses necesarios para alcanzar objetivo_capital."""
        if not self.objetivo_capital:
            return None
        meses = 0
        while self.calcular_capital_futuro(meses) < self.objetivo_capital and meses < 1200:
            meses += 1
        return meses

    def __repr__(self) -> str:
        return f"<ProyeccionFinanciera usuario={self.id_usuario} fecha={self.fecha_generacion}>"
