"""Regla R3: Clasificación del semáforo.

Verde: Días Transcurridos <= Meta Días.
Amarillo: Días Transcurridos > Meta Días y Días Transcurridos <= (Meta Días + 2).
Rojo: Días Transcurridos > (Meta Días + 2).
"""

from app.services.regla_r2 import META_DIAS

VERDE = "Verde"
AMARILLO = "Amarillo"
ROJO = "Rojo"


def clasificar_semaforo(dias_transcurridos: int | None, meta_dias: int = META_DIAS) -> str | None:
    """Clasifica una vacante en Verde, Amarillo o Rojo según los días transcurridos y la meta.

    Args:
        dias_transcurridos: Días transcurridos calculados por la regla R1.
        meta_días: Meta en días (constante, por defecto 10).

    Returns:
        "Verde", "Amarillo" o "Rojo", o None si días_transcurridos es None.
    """
    if dias_transcurridos is None:
        return None

    if dias_transcurridos <= meta_dias:
        return VERDE

    if dias_transcurridos <= meta_dias + 2:
        return AMARILLO

    return ROJO


def clasificar_semaforo_fila(fila: dict, dias_transcurridos: int | None = None) -> str | None:
    """Clasifica el semáforo para una fila del insumo.

    Args:
        fila: Diccionario con los datos de una fila del Excel.
        dias_transcurridos: Días transcurridos ya calculados (si es None, se calculan con R1).

    Returns:
        "Verde", "Amarillo" o "Rojo", o None si no hay días transcurridos.
    """
    from app.services.regla_r1 import calcular_dias_transcurridos_fila

    if dias_transcurridos is None:
        dias_transcurridos = calcular_dias_transcurridos_fila(fila)

    return clasificar_semaforo(dias_transcurridos, meta_dias=META_DIAS)


if __name__ == "__main__":
    # Pruebas con los límites del semáforo (Meta = 10)
    # Verde: <= 10
    assert clasificar_semaforo(10) == VERDE, "10 debe ser Verde"
    assert clasificar_semaforo(5) == VERDE, "5 debe ser Verde"
    assert clasificar_semaforo(0) == VERDE, "0 debe ser Verde"

    # Amarillo: > 10 y <= 12
    assert clasificar_semaforo(11) == AMARILLO, "11 debe ser Amarillo"
    assert clasificar_semaforo(12) == AMARILLO, "12 debe ser Amarillo"

    # Rojo: > 12
    assert clasificar_semaforo(13) == ROJO, "13 debe ser Rojo"
    assert clasificar_semaforo(14) == ROJO, "14 debe ser Rojo (Caso 2 REQ-002)"
    assert clasificar_semaforo(100) == ROJO, "100 debe ser Rojo"

    # None
    assert clasificar_semaforo(None) is None, "None debe retornar None"

    print("Pruebas de R3 pasadas correctamente.")
    print("Caso 2 (REQ-002): 14 días ->", clasificar_semaforo(14), "(esperado: Rojo)")
