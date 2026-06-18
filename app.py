from flask import Flask, render_template, url_for
from extensions import db
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///fico.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

db.init_app(app)

# importo rutas
from controllers.auth import register_routes as auth_routes
from controllers.dashboard import register_routes as dashboard_routes
from controllers.transacciones import register_routes as transacciones_routes
from controllers.presupuestos import register_routes as presupuestos_routes
from controllers.objetivos import register_routes as objetivos_routes
from controllers.reportes import register_routes as reportes_routes
from controllers.simulador import register_routes as simulador_routes
from controllers.chatbot import register_routes as chatbot_routes

auth_routes(app)
dashboard_routes(app)
transacciones_routes(app)
presupuestos_routes(app)
objetivos_routes(app)
reportes_routes(app)
simulador_routes(app)
chatbot_routes(app)

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
    return render_template(
        'public/simulador.html',
        valores={},
        resultado=None,
        form_action=url_for("calcular_simulador_publico"),
        contexto="publico",
    )


if __name__ == '__main__':
    app.run(debug=True)










