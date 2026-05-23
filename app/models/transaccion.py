from app import db
from datetime import date


class Transaccion(db.Model):
    __tablename__ = "transaccion"

    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario     = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_categoria   = db.Column(db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=True)
    tipo           = db.Column(db.Enum("ingreso", "egreso", name="tipo_transaccion"), nullable=False)
    monto          = db.Column(db.Float, nullable=False)
    fecha          = db.Column(db.Date, nullable=False, default=date.today)
    descripcion    = db.Column(db.String(255), nullable=True)
    es_recurrente  = db.Column(db.Boolean, default=False)

    # Campos específicos por tipo (nullable porque dependen del tipo)
    fuente         = db.Column(db.String(100), nullable=True)   # solo Ingreso
    tipo_gasto     = db.Column(db.String(100), nullable=True)   # solo Egreso

    # Relaciones
    usuario   = db.relationship("Usuario",   back_populates="transacciones")
    categoria = db.relationship("Categoria", back_populates="transacciones")

    def calcular_impacto(self) -> float:
        """Retorna positivo si es ingreso, negativo si es egreso."""
        return self.monto if self.tipo == "ingreso" else -self.monto

    def to_dict(self) -> dict:
        return {
            "id":          self.id_transaccion,
            "tipo":        self.tipo,
            "monto":       self.monto,
            "fecha":       self.fecha.isoformat(),
            "descripcion": self.descripcion,
            "categoria":   self.categoria.nombre if self.categoria else None,
            "recurrente":  self.es_recurrente,
        }

    def __repr__(self) -> str:
        return f"<Transaccion {self.tipo} ${self.monto} {self.fecha}>"
