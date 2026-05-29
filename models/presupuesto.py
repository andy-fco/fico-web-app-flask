from extensions import db
from datetime import date, timedelta
from models.transaccion import Transaccion


class Presupuesto(db.Model):
    __tablename__ = "presupuesto"

    id_presupuesto = db.Column(db.Integer, primary_key=True)
    id_usuario     = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    categoria      = db.Column(db.String(80), nullable=False)
    limite_gasto   = db.Column(db.Numeric(12, 2), nullable=False)
    moneda         = db.Column(db.Enum("ARS", "USD", name="moneda"), nullable=False, default="ARS")
    periodo        = db.Column(db.Enum("semana", "mes", "año", name="periodo_presupuesto"), nullable=False)
    fecha_inicio   = db.Column(db.Date, nullable=False, default=date.today)
    fecha_fin      = db.Column(db.Date, nullable=True)
    activo         = db.Column(db.Boolean, nullable=False, default=True)

    usuario = db.relationship("Usuario", back_populates="presupuestos")

    def get_periodo_actual(self) -> tuple[date, date]:
        hoy = date.today()

        if hoy < self.fecha_inicio:
            return self.fecha_inicio, self.fecha_inicio

        if self.fecha_fin is not None and hoy > self.fecha_fin:
            hoy = self.fecha_fin

        if self.periodo == "semana":
            dias_transcurridos = (hoy - self.fecha_inicio).days
            semanas_transcurridas = dias_transcurridos // 7
            inicio = self.fecha_inicio + timedelta(weeks=semanas_transcurridas)
            fin = inicio + timedelta(days=6)

        elif self.periodo == "mes":
            meses_transcurridos = (
                (hoy.year - self.fecha_inicio.year) * 12
                + (hoy.month - self.fecha_inicio.month)
            )

            year = self.fecha_inicio.year + (self.fecha_inicio.month - 1 + meses_transcurridos) // 12
            month = (self.fecha_inicio.month - 1 + meses_transcurridos) % 12 + 1

            inicio = date(year, month, self.fecha_inicio.day)

            if month == 12:
                siguiente_mes = date(year + 1, 1, 1)
            else:
                siguiente_mes = date(year, month + 1, 1)

            fin = siguiente_mes - timedelta(days=1)

        else:
            años_transcurridos = hoy.year - self.fecha_inicio.year
            inicio = date(self.fecha_inicio.year + años_transcurridos, self.fecha_inicio.month, self.fecha_inicio.day)
            fin = date(inicio.year + 1, inicio.month, inicio.day) - timedelta(days=1)

        if self.fecha_fin is not None and fin > self.fecha_fin:
            fin = self.fecha_fin

        return inicio, fin

    def get_gasto_actual(self) -> float:
        inicio, fin = self.get_periodo_actual()

        total = db.session.query(db.func.sum(Transaccion.monto)).filter(
            Transaccion.id_usuario == self.id_usuario,
            Transaccion.tipo == "egreso",
            Transaccion.categoria == self.categoria,
            Transaccion.moneda == self.moneda,
            Transaccion.fecha >= inicio,
            Transaccion.fecha <= fin,
        ).scalar()

        return float(total or 0)

    def get_porcentaje_usado(self) -> float:
        if self.limite_gasto == 0:
            return 0.0

        return round((self.get_gasto_actual() / float(self.limite_gasto)) * 100, 2)

    def esta_sobrepasado(self) -> bool:
        return self.get_gasto_actual() > float(self.limite_gasto)

    def get_alerta(self) -> str | None:
        pct = self.get_porcentaje_usado()

        if pct >= 100:
            return f"Superaste el límite de {self.categoria} ({pct:.0f}%)"

        if pct >= 80:
            return f"Estás cerca del límite de {self.categoria} ({pct:.0f}%)"

        return None

    def __repr__(self) -> str:
        return f"<Presupuesto {self.categoria} ${self.limite_gasto}>"