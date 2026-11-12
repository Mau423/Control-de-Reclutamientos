"""Regla R1: Calcular Días Transcurridos = Fecha Cierre - Fecha Requisición.

Si Fecha Cierre está vacía, se utiliza la Fecha Actual del sistema.
Fecha Requisición se toma de la columna "Fecha ingreso, ascenso o traslado".
Fecha Cierre se toma de la columna "Cierre proceso reclutamiento".
"""

from datetime import datetime


def _parse_fecha(valor) -> datetime | None:
    """Intenta convertir un valor a datetime.

    Acepta objetos datetime directamente, o strings en formato DD/MM/AAAA o ISO.
    Retorna None si no se puede convertir.
    """
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        valor = valor.strip()
        if not valor:
            return None
        # Intentar formatos comunes
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(valor, fmt)
            except ValueError:
                continue
    return None


def calcular_dias_transcurridos(fecha_requisicion, fecha_cierre=None) -> int | None:
    """Calcula los días transcurridos entre la fecha de requisición y la fecha de cierre.

    Args:
        fecha_requisicion: Fecha de requisición (datetime, string o None).
        fecha_cierre: Fecha de cierre (datetime, string o None). Si es None o vacía, se usa la fecha actual.

    Returns:
        Número de días transcurridos (int), o None si la fecha de requisición es inválida o no se puede convertir.

    Raises:
        ValueError: Si fecha_requisicion no se puede convertir a datetime.
    """
    fecha_req = _parse_fecha(fecha_requisicion)
    if fecha_req is None:
        return None

    # Si fecha_cierre está vacía o es None, usar fecha actual del sistema
    fecha_cier = _parse_fecha(fecha_cierre)
    if fecha_cier is None:
        fecha_cier = datetime.now()

    # Calcular diferencia en días (días calendario, según supuesto S3)
    delta = fecha_cier - fecha_req
    return delta.days


def calcular_dias_transcurridos_fila(fila: dict) -> int | None:
    """Calcula Días Transcurridos para una fila del insumo.

    Lee las columnas 'Fecha ingreso, ascenso o traslado' y 'Cierre proceso reclutamiento'
    del diccionario de la fila.

    Args:
        fila: Diccionario con los datos de una fila del Excel.

    Returns:
        Número de días transcurridos, o None si no hay fecha de requisición.
    """
    fecha_requisicion = fila.get("Fecha ingreso, ascenso o traslado")
    fecha_cierre = fila.get("Cierre proceso reclutamiento")
    return calcular_dias_transcurridos(fecha_requisicion, fecha_cierre)


if __name__ == "__main__":
    # Prueba rápida con el Caso 2 de las cifras de control (REQ-002)
    # Fecha Inicio: 01/03/2026, Fecha Cierre: 15/03/2026 -> Esperado: 14 días
    from datetime import datetime

    fecha_inicio = datetime(2026, 3, 1)
    fecha_cierre = datetime(2026, 3, 15)
    dias = calcular_dias_transcurridos(fecha_inicio, fecha_cierre)
    print(f"Caso 2 (REQ-002): {dias} días transcurridos (esperado: 14)")
    assert dias == 14, f"Se esperaban 14 días, se obtuvieron {dias}"

    # Prueba con fecha de cierre vacía (debe usar fecha actual)
    dias_sin_cierre = calcular_dias_transcurridos(fecha_inicio)
    print(f"Sin fecha de cierre: {dias_sin_cierre} días (usando fecha actual)")
    assert dias_sin_cierre is not None

    print("Pruebas de R1 pasadas correctamente.")
