"""ControlVacantes - Aplicación web de RRHH para auditoría de vacantes de reclutamiento."""

import os
from pathlib import Path

from flask import Flask

from app.controllers.auth import auth_bp
from app.controllers.vacantes import vacantes_bp


def _crear_directorios_instancia(app: Flask) -> None:
    """Crea los directorios de instancia necesarios para la app en producción."""
    instance_path = Path(app.instance_path)
    for subdir in ["uploads", "resultados", "exports"]:
        (instance_path / subdir).mkdir(parents=True, exist_ok=True)


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

    # Credenciales de acceso (sin base de datos, desde variables de entorno)
    app.config["APP_USUARIO"] = os.getenv("APP_USUARIO")
    app.config["APP_CLAVE"] = os.getenv("APP_CLAVE")

    # Crear directorios de instancia al iniciar (importante en Render)
    _crear_directorios_instancia(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(vacantes_bp)

    @app.get("/health")
    def health():
        """Endpoint de salud para verificar que la app está corriendo."""
        return {"status": "ok", "app": "ControlVacantes"}

    return app
