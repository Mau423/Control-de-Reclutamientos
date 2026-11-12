"""ControlVacantes - Aplicación web de RRHH para auditoría de vacantes de reclutamiento."""

import os

from flask import Flask

from app.controllers.vacantes import vacantes_bp


def create_app() -> Flask:
    """Crea y configura la aplicación Flask.

    Registra blueprints, carga variables de entorno desde .env
    y retorna la instancia de la app lista para usar.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Cargar configuración desde variables de entorno (se lee .env)
    app.config.from_prefixed_env()

    # Clave secreta para sesiones (obligatoria para usar session en Flask)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-cambiar-en-produccion")

    # Registrar blueprint de controladores de vacantes
    app.register_blueprint(vacantes_bp)

    @app.get("/health")
    def health():
        """Endpoint de salud para verificar que la app está corriendo."""
        return {"status": "ok", "app": "ControlVacantes"}

    return app
