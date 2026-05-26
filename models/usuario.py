from extensions import db
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario        = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(100), nullable=False)
    email             = db.Column(db.String(150), nullable=False, unique=True)
    password_hash     = db.Column(db.String(255), nullable=False)
    moneda_principal  = db.Column(db.String(10), nullable=False, default="ARS")
    fecha_registro    = db.Column(db.Date, nullable=False, default=date.today)

    # Relaciones
    transacciones  = db.relationship("Transaccion",        back_populates="usuario", cascade="all, delete-orphan")
    categorias     = db.relationship("Categoria",          back_populates="usuario", cascade="all, delete-orphan")
    presupuestos   = db.relationship("Presupuesto",        back_populates="usuario", cascade="all, delete-orphan")
    objetivos      = db.relationship("ObjetivoAhorro",     back_populates="usuario", cascade="all, delete-orphan")
    proyecciones   = db.relationship("ProyeccionFinanciera", back_populates="usuario", cascade="all, delete-orphan")
    simulaciones   = db.relationship("SimulacionIF",       back_populates="usuario", cascade="all, delete-orphan")
    conversaciones = db.relationship("Conversacion",       back_populates="usuario", cascade="all, delete-orphan")
    alertas        = db.relationship("Alerta",             back_populates="usuario", cascade="all, delete-orphan")

    # Métodos de contraseña
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Métodos de negocio
    def get_saldo_total(self) -> float:
        ingresos = sum(t.monto for t in self.transacciones if t.tipo == "ingreso")
        egresos  = sum(t.monto for t in self.transacciones if t.tipo == "egreso")
        return ingresos - egresos

    def __repr__(self) -> str:
        return f"<Usuario {self.email}>"
