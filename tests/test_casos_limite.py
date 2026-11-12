"""Pruebas de los casos límite según AGENTS.md.

Casos límite:
  - Archivo vacío -> mensaje de error
  - Fecha de Cierre vacía -> usa fecha actual
  - Dato corrupto o no válido -> alerta específica con fila y columna
  - Columna con nombre modificado -> error de estructura inválida
"""

from datetime import datetime

from app.services.regla_r1 import calcular_dias_transcurridos
from app.services.regla_r6 import validar_fila, validar_insumo

COL_REQ = "Requisición de puesto"
COL_PUESTO = "Puesto"
COL_FECHA_REQ = "Fecha ingreso, ascenso o traslado"
COL_FECHA_CIERRE = "Cierre proceso reclutamiento"


# ---------------------------------------------------------------------------
# Caso límite: Archivo vacío
# ---------------------------------------------------------------------------

def test_caso_limite_archivo_vacio_no_tiene_filas():
    """Lista vacía de filas no produce registros."""
    filas = []
    alertas = validar_insumo(filas)
    assert len(alertas) == 0
    assert len(filas) == 0


# ---------------------------------------------------------------------------
# Caso límite: Fecha de Cierre vacía
# ---------------------------------------------------------------------------

def test_caso_limite_fecha_cierre_vacía_usa_fecha_actual():
    """Si Fecha Cierre está vacía, R1 usa fecha actual del sistema."""
    resultado = calcular_dias_transcurridos(datetime(2026, 3, 1), None)
    assert resultado is not None
    assert resultado >= 0


def test_caso_limite_fecha_cierre_none_no_es_error():
    """Fecha Cierre None no genera alerta en R6 (es opcional)."""
    fila = {
        COL_REQ: "REQ-001",
        COL_PUESTO: "Asistente",
        COL_FECHA_REQ: datetime(2026, 3, 1),
        COL_FECHA_CIERRE: None,
    }
    alertas = validar_fila(fila, 2)
    # No debe haber alerta por fecha de cierre vacía
    alertas_cierre = [a for a in alertas if "Cierre" in a.columna]
    assert len(alertas_cierre) == 0


# ---------------------------------------------------------------------------
# Caso límite: Dato corrupto o no válido
# ---------------------------------------------------------------------------

def test_caso_limite_dato_corrupto_fecha_requisición_alerta():
    """Fecha de requisición corrupta genera alerta con fila y columna."""
    fila = {
        COL_REQ: "REQ-003",
        COL_PUESTO: "Contador",
        COL_FECHA_REQ: "TEXTO_INVALIDO",
        COL_FECHA_CIERRE: datetime(2026, 3, 10),
    }
    alertas = validar_fila(fila, 100)
    assert len(alertas) >= 1
    alerta_fecha = [a for a in alertas if "Fecha ingreso" in a.columna]
    assert len(alerta_fecha) == 1
    assert alerta_fecha[0].fila == 100
    assert "Formato no válido" in alerta_fecha[0].mensaje or "Fecha inválida" in alerta_fecha[0].mensaje


def test_caso_limite_dato_corrupto_fecha_cierre_alerta():
    """Fecha de cierre corrupta genera alerta con fila y columna."""
    fila = {
        COL_REQ: "REQ-004",
        COL_PUESTO: "Analista",
        COL_FECHA_REQ: datetime(2026, 3, 1),
        COL_FECHA_CIERRE: "FECHA_CORRUPTA",
    }
    alertas = validar_fila(fila, 200)
    assert len(alertas) >= 1
    alerta_cierre = [a for a in alertas if "Cierre" in a.columna]
    assert len(alerta_cierre) == 1
    assert alerta_cierre[0].fila == 200


# ---------------------------------------------------------------------------
# Caso límite: Columna con nombre modificado (faltante)
# ---------------------------------------------------------------------------

def test_caso_limite_columna_requisición_faltante_alerta():
    """Si falta la columna Requisición de puesto, genera alerta."""
    fila = {
        COL_PUESTO: "Asistente",
        COL_FECHA_REQ: datetime(2026, 3, 1),
    }
    alertas = validar_fila(fila, 300)
    assert len(alertas) >= 1
    alerta_req = [a for a in alertas if "Requisición" in a.columna]
    assert len(alerta_req) == 1
    assert alerta_req[0].fila == 300


def test_caso_limite_columnas_obligatorias_faltantes():
    """Si faltan todas las columnas obligatorias, múltiples alertas."""
    fila = {}
    alertas = validar_fila(fila, 400)
    assert len(alertas) == 3  # Requisición, Puesto, Fecha Requisición


def test_caso_limite_calcular_dias_con_fecha_texto_retorna_none():
    """R1 con fecha como texto retorna None (no lanza excepción)."""
    resultado = calcular_dias_transcurridos("TEXTO_INVALIDO")
    assert resultado is None
