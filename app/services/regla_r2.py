"""Regla R2: Calcular Días Exceso = Días Transcurridos - Meta Días.

Meta Días = 10 (valor constante, no existe como columna en el Excel).
"""

META_DIAS = 10


def calcular_dias_exceso(dias_transcurridos: int | None, meta_dias: int = META_DIAS) -> int | None:
    """Calcula los días de exceso sobre la meta establecida.

    Args:
        dias_transcurridos: Días transcurridos calculados por la regla R1.
        meta_días: Meta en días (constante, por defecto 10).

    Returns:
        Días exceso (int), o None si días_transcurridos es None.
    """
    if dias_transcurridos is None:
        return None

    return dias_transcurridos - meta_dias


def calcular_dias_exceso_fila(fila: dict, dias_transcurridos: int | None = None) -> int | None:
    """Calcula Días Exceso para una fila del insumo.

    Args:
        fila: Diccionario con los datos de una fila del Excel (no se usa directamente,
              se incluye para consistencia con el patrón de las demás reglas).
        dias_transcurridos: Días transcurridos ya calculados (si es None, se calculan con R1).

    Returns:
        Días exceso, o None si no hay días transcurridos.
    """
    from app.services.regla_r1 import calcular_dias_transcurridos_fila

    if dias_transcurridos is None:
        dias_transcurridos = calcular_dias_transcurridos_fila(fila)

    return calcular_dias_exceso(dias_transcurridos, meta_dias=META_DIAS)


if __name__ == "__main__":
    # Prueba con el Caso 2 de las cifras de control (REQ-002)
    # Días Transcurridos: 14, Meta: 10 -> Esperado: Días Exceso = 4
    exceso = calcular_dias_exceso(14)
    print(f"Caso 2 (REQ-002): {exceso} días exceso (esperado: 4)")
    assert exceso == 4, f"Se esperaban 4 días exceso, se obtuvieron {exceso}"

    # Prueba con días transcurridos None
    exceso_none = calcular_dias_exceso(None)
    print(f"Sin días transcurridos: {exceso_none}")
    assert exceso_none is None

    # Prueba con meta personalizada
    exceso_meta5 = calcular_dias_exceso(14, meta_dias=5)
    print(f"Con meta 5: {exceso_meta5} días exceso (esperado: 9)")
    assert exceso_meta5 == 9

    print("Pruebas de R2 pasadas correctamente.")
