from app import db
from datetime import date


class Presupuesto(db.Model):
    __tablename__ = "presupuesto"

    id_presupuesto = db.Column(db.Integer, primary_key=True)
    id_usuario     = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_categoria   = db.Column(db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False)
    limite_gasto   = db.Column(db.Float, nullable=False)
    periodo        = db.Column(db.Enum("semana", "mes", "año", name="periodo_presupuesto"), nullable=False)
    fecha_inicio   = db.Column(db.Date, nullable=False, default=date.today)
    fecha_fin      = db.Column(db.Date, nullable=True)

    # Relaciones
    usuario   = db.relationship("Usuario",   back_populates="presupuestos")
    categoria = db.relationship("Categoria", back_populates="presupuestos")

    def get_gasto_actual(self) -> float:
        return sum(
            t.monto for t in self.categoria.transacciones
            if t.tipo == "egreso"
            and t.id_usuario == self.id_usuario
            and t.fecha >= self.fecha_inicio
            and (self.fecha_fin is None or t.fecha <= self.fecha_fin)
        )

    def get_porcentaje_usado(self) -> float:
        if self.limite_gasto == 0:
            return 0.0
        return round((self.get_gasto_actual() / self.limite_gasto) * 100, 2)

    def esta_sobrepasado(self) -> bool:
        return self.get_gasto_actual() > self.limite_gasto

    def get_alerta(self) -> str | None:
        pct = self.get_porcentaje_usado()
        if pct >= 100:
            return f"Superaste el limite de {self.categoria.nombre} ({pct:.0f}%)"
        if pct >= 80:
            return f"Estas cerca del limite de {self.categoria.nombre} ({pct:.0f}%)"
        return None

    def __repr__(self) -> str:
        return f"<Presupuesto {self.categoria.nombre} ${self.limite_gasto}>"
