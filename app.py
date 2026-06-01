from flask import Flask, render_template
from extensions import db
from datetime import timedelta
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fico.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

db.init_app(app)

# importo rutas
from routes.auth import register_routes as auth_routes
from routes.dashboard import register_routes as dashboard_routes
from routes.transacciones import register_routes as transacciones_routes
from routes.presupuestos import register_routes as presupuestos_routes
from routes.objetivos import register_routes as objetivos_routes
from routes.reportes import register_routes as reportes_routes
from routes.simulador import register_routes as simulador_routes

auth_routes(app)
dashboard_routes(app)
transacciones_routes(app)
presupuestos_routes(app)
objetivos_routes(app)
reportes_routes(app)
simulador_routes(app)

# creo tablas
with app.app_context():
    from models.usuario import Usuario
    from models.transaccion import Transaccion
    from models.presupuesto import Presupuesto
    from models.objetivo_ahorro import ObjetivoAhorro
    from models.simulacion_if import SimulacionIF
    db.create_all()


#----------RUTAS PÚBLICAS-----------#

@app.route('/')
def inicio():
    return render_template('public/index.html')

@app.route('/simulador')
def simulador():
    return render_template('public/simulador.html')


if __name__ == '__main__':
    app.run(debug=True)










