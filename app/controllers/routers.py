"""
Definición de rutas e inicialización de la aplicación Flask.
"""

from flask import Flask
from app.controllers.ui_controller import ui_bp
import os

def init_app():
    """Crea e inicializa la aplicación Flask con sus rutas."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    # Registro de blueprints
    app.register_blueprint(ui_bp)

    # Soporte para mensajes flash
    app.secret_key = "simplex_Secret_key"

    return app
