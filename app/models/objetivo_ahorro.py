from app import db
from datetime import date


class ObjetivoAhorro(db.Model):
    __tablename__ = "objetivo_ahorro"

    id_objetivo    = db.Column(db.Integer, primary_key=True)
    id_usuario     = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    nombre         = db.Column(db.String(100), nullable=False)
    monto_objetivo = db.Column(db.Float, nullable=False)
    monto_actual   = db.Column(db.Float, nullable=False, default=0.0)
    fecha_limite   = db.Column(db.Date, nullable=True)
    estado         = db.Column(db.Enum("activo", "logrado", name="estado_objetivo"), default="activo")

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="objetivos")

    def get_progreso(self) -> float:
        if self.monto_objetivo == 0:
            return 0.0
        return round((self.monto_actual / self.monto_objetivo) * 100, 2)

    def esta_completada(self) -> bool:
        return self.monto_actual >= self.monto_objetivo

    def aportar_monto(self, monto: float) -> None:
        self.monto_actual += monto
        if self.esta_completada():
            self.estado = "logrado"

    def dias_restantes(self) -> int | None:
        if self.fecha_limite is None:
            return None
        delta = self.fecha_limite - date.today()
        return max(delta.days, 0)

    def __repr__(self) -> str:
        return f"<ObjetivoAhorro {self.nombre} {self.get_progreso()}%>"
