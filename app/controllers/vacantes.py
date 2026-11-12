"""Controlador de carga y procesamiento de vacantes.

Orquesta la lectura del insumo y la aplicación de las reglas de negocio R1-R6.
Devuelve los datos procesados listos para ser consumidos por el frontend y el agente de IA.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    send_file,
    url_for,
)

from app.services.agente_ia import analizar_con_ia
from app.services.exportacion import exportar_a_excel
from app.services.lectura_insumos import leer_insumos
from app.services.regla_r1 import calcular_dias_transcurridos_fila
from app.services.regla_r2 import calcular_dias_exceso_fila
from app.services.regla_r3 import clasificar_semaforo_fila
from app.services.regla_r4 import filtrar_por_ejecutor, obtener_ejecutores_unicos
from app.services.regla_r6 import AlertaValidacion, validar_fila

vacantes_bp = Blueprint("vacantes", __name__)

# ---------------------------------------------------------------------------
# Control de acceso: exigir autenticación en todas las rutas de este blueprint
# ---------------------------------------------------------------------------


@vacantes_bp.before_request
def _requiere_autenticacion():
    """Redirige a /login si el usuario no ha iniciado sesión."""
    from flask import request

    if "usuario" not in session:
        return redirect(url_for("auth.login"))


# Directorio para almacenar resultados temporales de procesamiento
# Se resuelve en la primera solicitud usando current_app.instance_path
_RESULTADOS_DIR = None


def _get_resultados_dir() -> Path:
    """Retorna el directorio de resultados temporales, creándolo si es necesario."""
    global _RESULTADOS_DIR
    if _RESULTADOS_DIR is None:
        _RESULTADOS_DIR = Path(current_app.instance_path) / "resultados"
        _RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    return _RESULTADOS_DIR


def _serializar_fecha(valor):
    """Convierte un valor datetime a string ISO para almacenamiento."""
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M:%S")
    return valor


def _serializar_registro(registro: dict) -> dict:
    """Convierte un registro a un diccionario serializable a JSON."""
    return {clave: _serializar_fecha(valor) for clave, valor in registro.items()}


def _guardar_resultado(resultado: dict) -> str:
    """Guarda el resultado procesado en un archivo JSON temporal y retorna su ID."""
    resultados_dir = _get_resultados_dir()
    resultado_id = str(uuid.uuid4())
    ruta = resultados_dir / f"{resultado_id}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    return resultado_id


def _cargar_resultado(resultado_id: str) -> dict | None:
    """Carga un resultado procesado desde su archivo JSON temporal."""
    resultados_dir = _get_resultados_dir()
    ruta = resultados_dir / f"{resultado_id}.json"
    if not ruta.exists():
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _eliminar_resultado(resultado_id: str) -> None:
    """Elimina un archivo de resultado temporal."""
    resultados_dir = _get_resultados_dir()
    ruta = resultados_dir / f"{resultado_id}.json"
    if ruta.exists():
        ruta.unlink()


def procesar_insumo(ruta_archivo: str | None = None, ejecutor_filtro: str | None = None) -> dict:
    """Procesa el archivo de insumos aplicando todas las reglas de negocio.

    Flujo:
      1. Lee el insumo (hoja "Total").
      2. Valida cada fila (R6): detecta fechas inválidas y campos obligatorios vacíos.
      3. Para cada fila válida, calcula Días Transcurridos (R1).
      4. Calcula Días Exceso (R2).
      5. Clasifica semáforo (R3).
      6. Filtra por ejecutor si se solicita (R4).

    Args:
        ruta_archivo: Ruta opcional al archivo de insumos.
        ejecutor_filtro: Nombre del ejecutor para filtrar (None = todos).

    Returns:
        Diccionario con:
          - 'registros': lista de dicts con los datos procesados por fila.
          - 'alertas': lista de AlertaValidacion con problemas encontrados.
          - 'contadores': conteo de registros por estado de semáforo.
          - 'ejecutores_disponibles': lista de ejecutores únicos para filtros.
          - 'total_filas': número total de filas leídas.
          - 'filas_validas': número de filas sin alertas críticas.
    """
    filas_raw = leer_insumos(ruta_archivo)
    total_filas = len(filas_raw)

    # Paso 1: Validar todas las filas (R6)
    todas_alertas: list[AlertaValidacion] = []
    filas_con_alerta_critica: set[int] = set()

    for idx, fila in enumerate(filas_raw):
        numero_fila = idx + 2  # Fila 2 es la primera de datos (fila 1 = encabezados)
        alertas_fila = validar_fila(fila, numero_fila)
        todas_alertas.extend(alertas_fila)
        # Marcar fila como crítica si tiene alertas en campos obligatorios o fechas de requisición
        for a in alertas_fila:
            if "obligatorio" in a.mensaje or (
                "Fecha inválida" in a.mensaje and "Fecha ingreso" in a.columna
            ):
                filas_con_alerta_critica.add(idx)

    # Paso 2-5: Procesar filas válidas (R1, R2, R3)
    registros = []
    filas_validas = 0
    contadores = {"Verde": 0, "Amarillo": 0, "Rojo": 0, "Sin datos": 0}

    for idx, fila in enumerate(filas_raw):
        if idx in filas_con_alerta_critica:
            continue

        filas_validas += 1

        # R1: Días Transcurridos
        dias_transcurridos = calcular_dias_transcurridos_fila(fila)

        # R2: Días Exceso
        dias_exceso = calcular_dias_exceso_fila(fila, dias_transcurridos=dias_transcurridos)

        # R3: Semáforo
        semaforo = clasificar_semaforo_fila(fila, dias_transcurridos=dias_transcurridos)
        if semaforo is None:
            semaforo = "Sin datos"
        contadores[semaforo] = contadores.get(semaforo, 0) + 1

        registro = {
            "id_requisicion": str(fila.get("Requisición de puesto", "")).strip(),
            "puesto": str(fila.get("Puesto", "")).strip(),
            "ejecutor": str(fila.get("Ejecuta", "")).strip(),
            "fecha_requisicion": _serializar_fecha(fila.get("Fecha ingreso, ascenso o traslado")),
            "fecha_cierre": _serializar_fecha(fila.get("Cierre proceso reclutamiento")),
            "dias_transcurridos": dias_transcurridos,
            "meta_dias": 10,
            "dias_exceso": dias_exceso,
            "estado_semaforo": semaforo,
            "numero_fila": idx + 2,
        }
        registros.append(registro)

    # Paso 6: Filtrar por ejecutor si se solicita (R4)
    if ejecutor_filtro and ejecutor_filtro.strip():
        registros = filtrar_por_ejecutor(registros, ejecutor_filtro)

    # Ejecutores disponibles para el selector del frontend
    ejecutores_disponibles = obtener_ejecutores_unicos(filas_raw)

    return {
        "registros": registros,
        "alertas": [a.to_dict() for a in todas_alertas],
        "contadores": contadores,
        "ejecutores_disponibles": ejecutores_disponibles,
        "total_filas": total_filas,
        "filas_validas": filas_validas,
    }


# ---------------------------------------------------------------------------
# Rutas Flask (Blueprint)
# ---------------------------------------------------------------------------

@vacantes_bp.get("/")
def inicio():
    """Pantalla de inicio: formulario para cargar el archivo Excel."""
    return render_template("inicio.html")


@vacantes_bp.post("/cargar")
def cargar_archivo():
    """Recibe el archivo Excel, lo procesa y redirige a resultados."""
    if "archivo" not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for("vacantes.inicio"))

    archivo = request.files["archivo"]
    if archivo.filename == "":
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for("vacantes.inicio"))

    if not (archivo.filename.endswith(".xlsx") or archivo.filename.endswith(".csv")):
        flash("El archivo debe ser .xlsx o .csv.", "error")
        return redirect(url_for("vacantes.inicio"))

    # Guardar archivo subido temporalmente
    upload_dir = Path(current_app.instance_path) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{uuid.uuid4().hex}_{archivo.filename}"
    ruta_guardado = upload_dir / nombre_archivo
    archivo.save(ruta_guardado)

    # Procesar el insumo (aplica R1-R6)
    try:
        resultado = procesar_insumo(ruta_archivo=str(ruta_guardado))
    except Exception as exc:
        flash(f"Error al procesar el archivo: {exc}", "error")
        return redirect(url_for("vacantes.inicio"))

    # Guardar resultados en archivo temporal (evita límite de sesión de cookies)
    resultado_id = _guardar_resultado(resultado)
    session["resultado_id"] = resultado_id

    flash(
        f"Archivo procesado: {resultado['filas_validas']} de {resultado['total_filas']} filas válidas.",
        "success",
    )
    return redirect(url_for("vacantes.resultados"))


@vacantes_bp.get("/resultados")
def resultados():
    """Pantalla de resultados: contadores, tabla, filtros y exportación."""
    resultado_id = session.get("resultado_id")
    if not resultado_id:
        flash("No hay datos procesados. Cargue un archivo primero.", "warning")
        return redirect(url_for("vacantes.inicio"))

    resultado = _cargar_resultado(resultado_id)
    if not resultado:
        flash("Los datos procesados ya no están disponibles. Cargue el archivo nuevamente.", "error")
        return redirect(url_for("vacantes.inicio"))

    return render_template(
        "resultados.html",
        registros=resultado["registros"],
        alertas=resultado["alertas"],
        contadores=resultado["contadores"],
        ejecutores_disponibles=resultado["ejecutores_disponibles"],
        total_filas=resultado["total_filas"],
        filas_validas=resultado["filas_validas"],
    )


@vacantes_bp.get("/exportar")
def exportar():
    """Exporta la tabla procesada a Excel."""
    resultado_id = session.get("resultado_id")
    if not resultado_id:
        flash("No hay datos para exportar.", "warning")
        return redirect(url_for("vacantes.inicio"))

    resultado = _cargar_resultado(resultado_id)
    if not resultado:
        flash("Los datos procesados ya no están disponibles.", "error")
        return redirect(url_for("vacantes.inicio"))

    # Reconstruir registros desde sesión (ya serializados como strings)
    registros = resultado["registros"]

    export_dir = Path(current_app.instance_path) / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    ruta_salida = export_dir / f"controlvacantes_export_{uuid.uuid4().hex}.xlsx"

    try:
        # exportar_a_excel lee del insumo original; para usar los registros filtrados,
        # llamamos directamente con los datos ya procesados
        from app.services.exportacion import exportar_registros_a_excel

        exportar_registros_a_excel(registros, ruta_salida)
        flash("Exportación completada.", "success")
        return send_file(ruta_salida, as_attachment=True, download_name="controlvacantes_export.xlsx")
    except Exception as exc:
        flash(f"Error al exportar: {exc}", "error")
        return redirect(url_for("vacantes.resultados"))


@vacantes_bp.get("/analisis-ia/<id_requisicion>")
def analisis_ia(id_requisicion: str):
    """Devuelve el análisis IA en JSON para un registro específico."""
    resultado_id = session.get("resultado_id")
    if not resultado_id:
        return {"error": "No hay datos procesados."}, 404

    resultado = _cargar_resultado(resultado_id)
    if not resultado:
        return {"error": "Los datos procesados ya no están disponibles."}, 404

    for registro in resultado["registros"]:
        if registro["id_requisicion"] == id_requisicion:
            try:
                respuesta = analizar_con_ia(registro)
                return respuesta
            except ValueError as exc:
                return {"error": str(exc)}, 500
            except RuntimeError as exc:
                return {"error": str(exc)}, 500

    return {"error": "Registro no encontrado."}, 404


if __name__ == "__main__":
    # Prueba rápida con el insumo real
    resultado = procesar_insumo()
    print(f"Total filas: {resultado['total_filas']}")
    print(f"Filas válidas: {resultado['filas_validas']}")
    print(f"Alertas: {len(resultado['alertas'])}")
    print(f"Contadores: {resultado['contadores']}")
    print(f"Ejecutores disponibles: {resultado['ejecutores_disponibles']}")
    print()
    if resultado["registros"]:
        print("Primer registro:")
        r = resultado["registros"][0]
        for k, v in r.items():
            print(f"  {k}: {v}")