"""Regla R4: Permitir filtrado dinámico por la columna Ejecutor (mapeada a "Ejecuta").

Devuelve solo las filas cuyo valor en la columna "Ejecuta" coincida con el ejecutor solicitado.
"""

from app.services.lectura_insumos import leer_insumos


COLUMNA_EJECUTOR = "Ejecuta"


def filtrar_por_ejecutor(filas: list[dict], ejecutor: str | None) -> list[dict]:
    """Filtra una lista de filas por el valor de la columna "Ejecuta".

    Args:
        filas: Lista de diccionarios con los datos de las filas del Excel.
        ejecutor: Nombre del ejecutor a filtrar. Si es None o vacío, devuelve todas las filas sin filtrar.

    Returns:
        Lista de filas que coinciden con el ejecutor, o todas las filas si ejecutor es None/vacío.
    """
    if not ejecutor or not ejecutor.strip():
        return filas

    ejecutor_limpio = ejecutor.strip()
    return [
        fila for fila in filas
        if str(fila.get(COLUMNA_EJECUTOR, "")).strip() == ejecutor_limpio
    ]


def obtener_ejecutores_unicos(filas: list[dict]) -> list[str]:
    """Devuelve la lista de ejecutores únicos presentes en las filas.

    Útil para poblar el selector desplegable de la interfaz.

    Args:
        filas: Lista de diccionarios con los datos de las filas del Excel.

    Returns:
        Lista ordenada de nombres de ejecutores únicos (sin vacíos).
    """
    ejecutores = set()
    for fila in filas:
        valor = fila.get(COLUMNA_EJECUTOR)
        if valor is not None and str(valor).strip():
            ejecutores.add(str(valor).strip())
    return sorted(ejecutores)


def filtrar_insumos_por_ejecutor(ejecutor: str | None, ruta_archivo: str | None = None) -> list[dict]:
    """Lee el insumo completo y lo filtra por ejecutor en un solo paso.

    Args:
        ejecutor: Nombre del ejecutor a filtrar (None para todos).
        ruta_archivo: Ruta opcional al archivo de insumos.

    Returns:
        Lista de filas filtradas por ejecutor.
    """
    from app.services.lectura_insumos import leer_insumos

    filas = leer_insumos(ruta_archivo)
    return filtrar_por_ejecutor(filas, ejecutor)


if __name__ == "__main__":
    # Prueba rápida con los datos del insumo
    filas = leer_insumos()
    print(f"Total de filas: {len(filas)}")

    ejecutores = obtener_ejecutores_unicos(filas)
    print(f"Ejecutores únicos ({len(ejecutores)}): {ejecutores}")

    if ejecutores:
        primer_ejecutor = ejecutores[0]
        filas_filtradas = filtrar_por_ejecutor(filas, primer_ejecutor)
        print(f"Filas para '{primer_ejecutor}': {len(filas_filtradas)}")

    # Sin filtro devuelve todas
    todas = filtrar_por_ejecutor(filas, None)
    assert len(todas) == len(filas), "Sin filtro debe devolver todas las filas"
    print("Pruebas de R4 pasadas correctamente.")
