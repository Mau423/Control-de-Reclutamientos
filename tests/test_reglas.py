"""Pruebas de las reglas de negocio R1-R6 según AGENTS.md.

Cifras de control (Caso 2 - REQ-002):
  - Fecha Inicio: 01/03/2026
  - Fecha Cierre: 15/03/2026
  - Días Transcurridos: 14
  - Meta: 10 días
  - Días Exceso: 4
  - Estado: ROJA
"""

from datetime import datetime

from app.services.regla_r1 import calcular_dias_transcurridos, calcular_dias_transcurridos_fila
from app.services.regla_r2 import calcular_dias_exceso, calcular_dias_exceso_fila
from app.services.regla_r3 import clasificar_semaforo, clasificar_semaforo_fila
from app.services.regla_r4 import filtrar_por_ejecutor, obtener_ejecutores_unicos
from app.services.regla_r6 import validar_fila, validar_insumo, AlertaValidacion


# ---------------------------------------------------------------------------
# R1: Días Transcurridos = Fecha Cierre - Fecha Requisición
# ---------------------------------------------------------------------------

def test_r1_caso2_dias_transcurridos_14():
    """Caso 2 (REQ-002): 01/03/2026 a 15/03/2026 debe dar 14 días."""
    resultado = calcular_dias_transcurridos(
        datetime(2026, 3, 1), datetime(2026, 3, 15)
    )
    assert resultado == 14, f"Esperado 14 días, obtenido {resultado}"


def test_r1_fecha_cierre_vacía_usa_fecha_actual():
    """Si Fecha Cierre está vacía, se usa la fecha actual del sistema."""
    resultado = calcular_dias_transcurridos(datetime(2026, 3, 1))
    assert resultado is not None
    assert resultado >= 0  # Desde marzo 2026 hasta ahora debe ser positivo


def test_r1_fecha_requisición_none_retorna_none():
    """Si fecha de requisición es None, retorna None."""
    resultado = calcular_dias_transcurridos(None)
    assert resultado is None


def test_r1_fecha_requisición_invalida_retorna_none():
    """Si fecha de requisición no es datetime válido, retorna None."""
    resultado = calcular_dias_transcurridos("TEXTO_INVALIDO")
    assert resultado is None


def test_r1_fila_sin_fecha_retorna_none():
    """Fila sin fecha de requisición retorna None."""
    fila = {}
    resultado = calcular_dias_transcurridos_fila(fila)
    assert resultado is None


# ---------------------------------------------------------------------------
# R2: Días Exceso = Días Transcurridos - Meta Días (Meta = 10)
# ---------------------------------------------------------------------------

def test_r2_caso2_dias_exceso_4():
    """Caso 2 (REQ-002): 14 días - 10 meta = 4 días exceso."""
    resultado = calcular_dias_exceso(14)
    assert resultado == 4, f"Esperado 4 días exceso, obtenido {resultado}"


def test_r2_dias_transcurridos_none_retorna_none():
    """Si días transcurridos es None, retorna None."""
    resultado = calcular_dias_exceso(None)
    assert resultado is None


def test_r2_dias_menor_meta_retorna_negativo():
    """Si días transcurridos son menores a meta, exceso es negativo."""
    resultado = calcular_dias_exceso(5)
    assert resultado == -5


# ---------------------------------------------------------------------------
# R3: Clasificación semáforo
# ---------------------------------------------------------------------------

def test_r3_caso2_es_rojo():
    """Caso 2 (REQ-002): 14 días con meta 10 debe ser Rojo."""
    resultado = clasificar_semaforo(14)
    assert resultado == "Rojo", f"Esperado Rojo, obtenido {resultado}"


def test_r3_verde_días_iguales_meta():
    """Días transcurridos iguales a meta = Verde."""
    assert clasificar_semaforo(10) == "Verde"


def test_r3_verde_días_menores_meta():
    """Días transcurridos menores a meta = Verde."""
    assert clasificar_semaforo(5) == "Verde"


def test_r3_amarillo_meta_más_1():
    """Meta + 1 = Amarillo."""
    assert clasificar_semaforo(11) == "Amarillo"


def test_r3_amarillo_meta_más_2():
    """Meta + 2 = Amarillo."""
    assert clasificar_semaforo(12) == "Amarillo"


def test_r3_rojo_meta_más_3():
    """Meta + 3 = Rojo."""
    assert clasificar_semaforo(13) == "Rojo"


def test_r3_none_retorna_none():
    """Si días transcurridos es None, retorna None."""
    assert clasificar_semaforo(None) is None


# ---------------------------------------------------------------------------
# R4: Filtrado por Ejecutor
# ---------------------------------------------------------------------------

def test_r4_filtrar_por_ejecutor_devuelve_solo_su_filas():
    """Filtrar por un ejecutor debe devolver solo sus filas."""
    filas = [
        {"Ejecuta": "Ana", "Puesto": "Asistente"},
        {"Ejecuta": "Luis", "Puesto": "Desarrollador"},
        {"Ejecuta": "Ana", "Puesto": "Contador"},
    ]
    resultado = filtrar_por_ejecutor(filas, "Ana")
    assert len(resultado) == 2
    assert all(f["Ejecuta"] == "Ana" for f in resultado)


def test_r4_filtrar_none_devuelve_todas():
    """Si ejecutor es None, devuelve todas las filas."""
    filas = [{"Ejecuta": "Ana"}, {"Ejecuta": "Luis"}]
    resultado = filtrar_por_ejecutor(filas, None)
    assert len(resultado) == 2


def test_r4_filtrar_vacío_devuelve_todas():
    """Si ejecutor es string vacío, devuelve todas las filas."""
    filas = [{"Ejecuta": "Ana"}]
    resultado = filtrar_por_ejecutor(filas, "")
    assert len(resultado) == 1


def test_r4_obtener_ejecutores_unicos():
    """Debe devolver ejecutores únicos ordenados."""
    filas = [
        {"Ejecuta": "Luis"},
        {"Ejecuta": "Ana"},
        {"Ejecuta": "Ana"},
        {"Ejecuta": "Karina"},
    ]
    resultado = obtener_ejecutores_unicos(filas)
    assert resultado == ["Ana", "Karina", "Luis"]


# ---------------------------------------------------------------------------
# R6: Validación de fechas inválidas y campos obligatorios
# ---------------------------------------------------------------------------

COL_REQ = "Requisición de puesto"
COL_PUESTO = "Puesto"
COL_FECHA_REQ = "Fecha ingreso, ascenso o traslado"
COL_FECHA_CIERRE = "Cierre proceso reclutamiento"


def test_r6_fila_valida_no_tiene_alertas():
    """Una fila válida no debe generar alertas."""
    fila = {
        COL_REQ: "REQ-001",
        COL_PUESTO: "Asistente",
        COL_FECHA_REQ: datetime(2026, 3, 1),
        COL_FECHA_CIERRE: datetime(2026, 3, 8),
    }
    alertas = validar_fila(fila, 2)
    assert len(alertas) == 0


def test_r6_requisición_vacía_alerta():
    """Requisición de puesto vacía genera alerta."""
    fila = {
        COL_REQ: "",
        COL_PUESTO: "Asistente",
        COL_FECHA_REQ: datetime(2026, 3, 1),
    }
    alertas = validar_fila(fila, 3)
    assert len(alertas) >= 1
    assert any("Requisición de puesto" in a.columna for a in alertas)


def test_r6_puesto_none_alerta():
    """Puesto None genera alerta."""
    fila = {
        COL_REQ: "REQ-002",
        COL_PUESTO: None,
        COL_FECHA_REQ: datetime(2026, 3, 1),
    }
    alertas = validar_fila(fila, 4)
    assert len(alertas) >= 1
    assert any("Puesto" in a.columna for a in alertas)


def test_r6_fecha_requisición_texto_invalido_alerta():
    """Fecha de requisición como texto inválido genera alerta."""
    fila = {
        COL_REQ: "REQ-003",
        COL_PUESTO: "Contador",
        COL_FECHA_REQ: "TEXTO_INVALIDO",
    }
    alertas = validar_fila(fila, 5)
    assert len(alertas) >= 1
    assert any("Fecha ingreso" in a.columna for a in alertas)


def test_r6_alerta_tiene_fila_y_columna():
    """Cada alerta debe tener número de fila y nombre de columna."""
    fila = {
        COL_REQ: "",
        COL_PUESTO: None,
        COL_FECHA_REQ: None,
    }
    alertas = validar_fila(fila, 10)
    assert len(alertas) > 0
    for a in alertas:
        assert a.fila == 10
        assert a.columna is not None
        assert a.mensaje is not None


def test_r6_alerta_to_dict_retorna_diccionario():
    """to_dict() de AlertaValidacion retorna diccionario con fila, columna, mensaje."""
    a = AlertaValidacion(5, "Puesto", "Campo vacío")
    d = a.to_dict()
    assert d["fila"] == 5
    assert d["columna"] == "Puesto"
    assert d["mensaje"] == "Campo vacío"


# ---------------------------------------------------------------------------
# Cifras de control: Caso 2 (REQ-002)
# ---------------------------------------------------------------------------

def test_cifras_control_caso2_flujo_completo():
    """Flujo completo Caso 2: R1 -> R2 -> R3."""
    # R1: 14 días transcurridos
    dias = calcular_dias_transcurridos(
        datetime(2026, 3, 1), datetime(2026, 3, 15)
    )
    assert dias == 14

    # R2: 4 días exceso
    exceso = calcular_dias_exceso(dias)
    assert exceso == 4

    # R3: Rojo
    semaforo = clasificar_semaforo(dias)
    assert semaforo == "Rojo"

    print("\nCifras de control Caso 2 (REQ-002): OK")
    print(f"  Días Transcurridos: {dias} (esperado: 14)")
    print(f"  Días Exceso: {exceso} (esperado: 4)")
    print(f"  Estado Semáforo: {semaforo} (esperado: Rojo)")
