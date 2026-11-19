"""Servicio de lectura de insumos: lee la hoja "Total" de RECLUTAMIENTO.xlsx.

Devuelve las filas de datos con las 15 columnas del archivo fuente.
No modifica el archivo original de insumos.
Optimizado para consumir poca memoria usando openpyxl en modo read_only.
"""

from pathlib import Path

import openpyxl

# Ruta relativa al archivo de insumos (respetar la carpeta insumos, no modificar)
INSUMOS_PATH = Path(__file__).resolve().parent.parent.parent / "Insumos reclutamiento" / "RECLUTAMIENTO.xlsx"

HOJA_DATOS = "Total"
FILA_ENCABEZADOS = 6  # Fila donde están los nombres de columna en la hoja "Total"

# Nombres esperados de las 15 columnas (en orden, tal como aparecen en el archivo)
COLUMNAS_ESPERADAS = [
    "#",
    "Puesto",
    "Tipo de Puesto",
    "Número de plaza",
    "Estadística",
    "Razón de salida de colaborador a reemplazar",
    "Cantidad entrevistas",
    "Requisición de puesto",
    "Cierre proceso reclutamiento",
    "Cantidad días proceso reclutamiento",
    "Fecha ingreso, ascenso o traslado",
    "Ejecuta",
    "Movimiento",
    "Status",
    "Ingreso",
]


def leer_insumos(ruta_archivo: str | Path | None = None) -> list[dict]:
    """Lee la hoja "Total" del Excel de insumos y devuelve una lista de diccionarios.

    Cada diccionario representa una fila con las claves siendo los nombres
    de las 15 columnas del archivo fuente.

    Optimización de memoria: usa openpyxl en modo read_only=True y iter_rows(),
    que lee el archivo fila por fila en lugar de cargarlo todo en memoria.

    Args:
        ruta_archivo: Ruta al archivo .xlsx. Si es None, usa la ruta por defecto.

    Returns:
        Lista de diccionarios, uno por fila de datos.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si falta una columna obligatoria o la hoja no existe.
    """
    ruta = Path(ruta_archivo) if ruta_archivo else INSUMOS_PATH

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de insumos: {ruta}")

    # read_only=True evita cargar todo el libro en memoria; ideal para archivos grandes
    wb = openpyxl.load_workbook(ruta, data_only=True, read_only=True)

    try:
        if HOJA_DATOS not in wb.sheetnames:
            raise ValueError(f"La hoja '{HOJA_DATOS}' no existe en el archivo")

        ws = wb[HOJA_DATOS]

        # Leer encabezados de la fila FILA_ENCABEZADOS usando iter_rows (eficiente en memoria)
        encabezados = []
        for row in ws.iter_rows(min_row=FILA_ENCABEZADOS, max_row=FILA_ENCABEZADOS, values_only=True):
            for col_idx, valor in enumerate(row, start=1):
                if valor is not None:
                    encabezados.append((col_idx, str(valor)))

        # Mapear índice de columna -> nombre de encabezado (con strip para limpiar espacios)
        col_por_nombre = {str(nombre).strip(): col_idx for col_idx, nombre in encabezados}

        # Validar que existen todas las columnas obligatorias
        columnas_faltantes = [c for c in COLUMNAS_ESPERADAS if c not in col_por_nombre]
        if columnas_faltantes:
            raise ValueError(
                f"Faltan columnas obligatorias en la hoja '{HOJA_DATOS}': {columnas_faltantes}"
            )

        # Leer filas de datos (después de la fila de encabezados) usando iter_rows
        filas = []
        for row_idx, row in enumerate(
            ws.iter_rows(min_row=FILA_ENCABEZADOS + 1, values_only=True),
            start=FILA_ENCABEZADOS + 1,
        ):
            fila = {}
            fila_tiene_datos = False
            for nombre_col in COLUMNAS_ESPERADAS:
                col_idx = col_por_nombre[nombre_col]
                # col_idx es 1-based; row es 0-based
                valor = row[col_idx - 1] if col_idx - 1 < len(row) else None
                if valor is not None:
                    fila_tiene_datos = True
                fila[nombre_col] = valor
            if fila_tiene_datos:
                filas.append(fila)

        return filas
    finally:
        # Cerrar el workbook para liberar memoria inmediatamente
        wb.close()


def leer_primeras_n_filas(n: int = 3) -> list[dict]:
    """Devuelve las primeras n filas de datos del insumo (útil para pruebas rápidas)."""
    todas = leer_insumos()
    return todas[:n]


if __name__ == "__main__":
    filas = leer_primeras_n_filas(3)
    for i, fila in enumerate(filas, 1):
        print(f"Fila {i}: {fila}")
