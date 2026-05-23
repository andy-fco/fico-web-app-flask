from app import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    id_categoria      = db.Column(db.Integer, primary_key=True)
    id_usuario        = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    nombre            = db.Column(db.String(100), nullable=False)
    tipo              = db.Column(db.Enum("ingreso", "egreso", name="tipo_categoria"), nullable=False)
    color             = db.Column(db.String(7), nullable=False, default="#2cd195")
    es_predeterminada = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario      = db.relationship("Usuario",     back_populates="categorias")
    transacciones = db.relationship("Transaccion", back_populates="categoria")
    presupuestos  = db.relationship("Presupuesto", back_populates="categoria", cascade="all, delete-orphan")

    def get_gasto_total(self) -> float:
        return sum(t.monto for t in self.transacciones if t.tipo == "egreso")

    def __repr__(self) -> str:
        return f"<Categoria {self.nombre}>"
