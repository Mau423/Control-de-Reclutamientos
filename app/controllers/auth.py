"""Controlador de autenticación simple sin base de datos.

Lee el usuario y la clave de las variables de entorno APP_USUARIO y APP_CLAVE.
Usa la sesión de Flask para mantener el estado de autenticación.
"""

import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

auth_bp = Blueprint("auth", __name__)


def _credenciales_validas(usuario: str, clave: str) -> bool:
    """Compara las credenciales recibidas con las variables de entorno."""
    app_usuario = (
        current_app.config.get("APP_USUARIO") or os.getenv("APP_USUARIO")
    )
    app_clave = current_app.config.get("APP_CLAVE") or os.getenv("APP_CLAVE")

    if not app_usuario or not app_clave:
        return False

    return usuario == app_usuario and clave == app_clave


@auth_bp.get("/login")
def login():
    """Muestra el formulario de ingreso."""
    if "usuario" in session:
        return redirect(url_for("vacantes.inicio"))
    return render_template("login.html")


@auth_bp.post("/login")
def autenticar():
    """Valida las credenciales y crea la sesión."""
    usuario = request.form.get("usuario", "").strip()
    clave = request.form.get("clave", "").strip()

    if _credenciales_validas(usuario, clave):
        session["usuario"] = usuario
        session.permanent = False
        flash("Sesión iniciada correctamente.", "success")
        return redirect(url_for("vacantes.inicio"))

    flash("Usuario o contraseña incorrectos", "error")
    return redirect(url_for("auth.login"))


@auth_bp.get("/salir")
def salir():
    """Cierra la sesión del usuario."""
    session.pop("usuario", None)
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
