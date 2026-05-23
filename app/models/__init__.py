from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transacciones import transacciones_bp
    from app.routes.categorias import categorias_bp
    from app.routes.presupuestos import presupuestos_bp
    from app.routes.objetivos import objetivos_bp
    from app.routes.reportes import reportes_bp
    from app.routes.simulador import simulador_bp
    from app.routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transacciones_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(presupuestos_bp)
    app.register_blueprint(objetivos_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(simulador_bp)
    app.register_blueprint(chatbot_bp)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app
