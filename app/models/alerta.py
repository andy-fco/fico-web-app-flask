from app import db
from datetime import datetime


class Alerta(db.Model):
    __tablename__ = "alerta"

    id_alerta  = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    tipo       = db.Column(db.Enum("gasto_excedido", "bajo_ahorro", "meta_proxima",
                                   name="tipo_alerta"), nullable=False)
    mensaje    = db.Column(db.String(255), nullable=False)
    fecha      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leida      = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="alertas")

    def marcar_leida(self) -> None:
        self.leida = True

    def __repr__(self) -> str:
        return f"<Alerta {self.tipo} leida={self.leida}>"
