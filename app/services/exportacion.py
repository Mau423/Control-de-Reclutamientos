"""Exportación de resultados a Excel.

Descarga la tabla procesada junto con los estados de alerta en formato .xlsx.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


COLUMNAS_EXPORTACION = [
    ("id_requisicion", "Requisición"),
    ("puesto", "Puesto"),
    ("ejecutor", "Ejecutor"),
    ("fecha_requisicion", "Fecha Requisición"),
    ("fecha_cierre", "Fecha Cierre"),
    ("dias_transcurridos", "Días Transcurridos"),
    ("meta_dias", "Meta Días"),
    ("dias_exceso", "Días Exceso"),
    ("estado_semaforo", "Estado Semáforo"),
]

# Colores para el semáforo en Excel
COLOR_VERDE = "C6EFCE"
COLOR_AMARILLO = "FFEB9C"
COLOR_ROJO = "FFC7CE"


def exportar_a_excel(ruta_salida: str | Path, ruta_archivo: str | None = None, ejecutor_filtro: str | None = None) -> Path:
    """Exporta los resultados procesados a un archivo .xlsx.

    Args:
        ruta_salida: Ruta donde se guardará el archivo .xlsx de salida.
        ruta_archivo: Ruta opcional al archivo de insumos de entrada.
        ejecutor_filtro: Nombre del ejecutor para filtrar (None = todos).

    Returns:
        Ruta al archivo .xlsx generado.
    """
    from app.controllers.vacantes import procesar_insumo

    resultado = procesar_insumo(ruta_archivo=ruta_archivo, ejecutor_filtro=ejecutor_filtro)
    registros = resultado["registros"]
    alertas = resultado["alertas"]

    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados ControlVacantes"

    # Escribir encabezados
    for col_idx, (_, nombre_amigable) in enumerate(COLUMNAS_EXPORTACION, 1):
        celda = ws.cell(row=1, column=col_idx, value=nombre_amigable)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        celda.alignment = Alignment(horizontal="center", vertical="center")

    # Escribir datos
    for row_idx, registro in enumerate(registros, 2):
        for col_idx, (clave, _) in enumerate(COLUMNAS_EXPORTACION, 1):
            valor = registro.get(clave)
            celda = ws.cell(row=row_idx, column=col_idx, value=valor)
            celda.alignment = Alignment(horizontal="center", vertical="center")

            # Color de fondo según semáforo
            if clave == "estado_semaforo":
                if valor == "Verde":
                    celda.fill = PatternFill(start_color=COLOR_VERDE, end_color=COLOR_VERDE, fill_type="solid")
                elif valor == "Amarillo":
                    celda.fill = PatternFill(start_color=COLOR_AMARILLO, end_color=COLOR_AMARILLO, fill_type="solid")
                elif valor == "Rojo":
                    celda.fill = PatternFill(start_color=COLOR_ROJO, end_color=COLOR_ROJO, fill_type="solid")

    # Ajustar ancho de columnas automáticamente
    for col_idx in range(1, len(COLUMNAS_EXPORTACION) + 1):
        letra = get_column_letter(col_idx)
        ws.column_dimensions[letra].width = 20

    # Hoja de alertas (segunda hoja)
    if alertas:
        ws_alertas = wb.create_sheet(title="Alertas")
        encabezados_alerta = ["Fila", "Columna", "Mensaje"]
        for col_idx, nombre in enumerate(encabezados_alerta, 1):
            celda = ws_alertas.cell(row=1, column=col_idx, value=nombre)
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")

        for row_idx, alerta in enumerate(alertas, 2):
            ws_alertas.cell(row=row_idx, column=1, value=alerta["fila"])
            ws_alertas.cell(row=row_idx, column=2, value=alerta["columna"])
            ws_alertas.cell(row=row_idx, column=3, value=alerta["mensaje"])

        for col_idx in range(1, 4):
            letra = get_column_letter(col_idx)
            ws_alertas.column_dimensions[letra].width = 30

    # Guardar archivo
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ruta_salida)

    return ruta_salida


def exportar_registros_a_excel(registros: list[dict], ruta_salida: str | Path) -> Path:
    """Exporta una lista de registros ya procesados a un archivo .xlsx.

    Args:
        registros: Lista de diccionarios con los datos ya procesados (claves:
            id_requisicion, puesto, ejecutor, fecha_requisicion, fecha_cierre,
            dias_transcurridos, meta_dias, dias_exceso, estado_semaforo).
        ruta_salida: Ruta donde se guardará el archivo .xlsx de salida.

    Returns:
        Ruta al archivo .xlsx generado.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados ControlVacantes"

    # Escribir encabezados
    for col_idx, (_, nombre_amigable) in enumerate(COLUMNAS_EXPORTACION, 1):
        celda = ws.cell(row=1, column=col_idx, value=nombre_amigable)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        celda.alignment = Alignment(horizontal="center", vertical="center")

    # Escribir datos
    COLOR_VERDE = "C6EFCE"
    COLOR_AMARILLO = "FFEB9C"
    COLOR_ROJO = "FFC7CE"

    for row_idx, registro in enumerate(registros, 2):
        for col_idx, (clave, _) in enumerate(COLUMNAS_EXPORTACION, 1):
            valor = registro.get(clave)
            celda = ws.cell(row=row_idx, column=col_idx, value=valor)
            celda.alignment = Alignment(horizontal="center", vertical="center")

            # Color de fondo según semáforo
            if clave == "estado_semaforo":
                if valor == "Verde":
                    celda.fill = PatternFill(start_color=COLOR_VERDE, end_color=COLOR_VERDE, fill_type="solid")
                elif valor == "Amarillo":
                    celda.fill = PatternFill(start_color=COLOR_AMARILLO, end_color=COLOR_AMARILLO, fill_type="solid")
                elif valor == "Rojo":
                    celda.fill = PatternFill(start_color=COLOR_ROJO, end_color=COLOR_ROJO, fill_type="solid")

    # Ajustar ancho de columnas automáticamente
    for col_idx in range(1, len(COLUMNAS_EXPORTACION) + 1):
        letra = get_column_letter(col_idx)
        ws.column_dimensions[letra].width = 20

    # Hoja de alertas (segunda hoja) - vacía para esta función
    ws_alertas = wb.create_sheet(title="Alertas")
    encabezados_alerta = ["Fila", "Columna", "Mensaje"]
    for col_idx, nombre in enumerate(encabezados_alerta, 1):
        celda = ws_alertas.cell(row=1, column=col_idx, value=nombre)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    for col_idx in range(1, 4):
        letra = get_column_letter(col_idx)
        ws_alertas.column_dimensions[letra].width = 30

    # Guardar archivo
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ruta_salida)

    return ruta_salida


if __name__ == "__main__":
    # Prueba rápida: exportar a un archivo de prueba
    ruta_salida = Path("resultado_prueba_exportacion.xlsx")
    ruta_generada = exportar_a_excel(ruta_salida)
    print(f"Archivo exportado: {ruta_generada}")
    print(f"Existe: {ruta_generada.exists()}")
    print(f"Tamaño: {ruta_generada.stat().st_size} bytes")

    # Limpiar archivo de prueba
    ruta_generada.unlink()
    print("Archivo de prueba eliminado.")

    print("Pruebas de exportación pasadas correctamente.")
