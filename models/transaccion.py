from extensions import db
from datetime import date


class Transaccion(db.Model):
    __tablename__ = "transaccion"

    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario     = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    tipo           = db.Column(db.Enum("ingreso", "egreso", name="tipo_transaccion"), nullable=False)
    monto          = db.Column(db.Numeric(12, 2), nullable=False)
    moneda         = db.Column(db.Enum("ARS", "USD", name="moneda"), nullable=False, default="ARS")
    categoria      = db.Column(db.String(80), nullable=False)
    fecha          = db.Column(db.Date, nullable=False, default=date.today)
    descripcion    = db.Column(db.String(255), nullable=True)
    es_recurrente  = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario   = db.relationship("Usuario",   back_populates="transacciones")


    def calcular_impacto(self) -> float:
        """Retorna positivo si es ingreso, negativo si es egreso."""
        return float(self.monto) if self.tipo == "ingreso" else -float(self.monto)

    def to_dict(self) -> dict:
        return {
            "id":          self.id_transaccion,
            "tipo":        self.tipo,
            "monto":       float(self.monto),
            "moneda":      self.moneda,
            "fecha":       self.fecha.isoformat(),
            "descripcion": self.descripcion,
            "categoria":   self.categoria,
            "recurrente":  self.es_recurrente,
        }

    def __repr__(self) -> str:
        return f"<Transaccion {self.tipo} ${self.monto} {self.fecha}>"
