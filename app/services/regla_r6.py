"""Regla R6: Detección de fechas inválidas y campos obligatorios vacíos.

Si una fila contiene fechas inválidas o campos obligatorios vacíos,
el código debe registrar una alerta específica con el número de fila
y columna correspondiente.

Campos obligatorios (según el contexto):
  - Requisición de puesto (ID Requisición)
  - Puesto
  - Fecha ingreso, ascenso o traslado (Fecha Requisición)

Fecha Cierre es opcional (puede estar vacía; se usa fecha actual del sistema).
"""

from datetime import datetime

from app.services.lectura_insumos import leer_insumos

COLUMNA_REQUISICION = "Requisición de puesto"
COLUMNA_PUESTO = "Puesto"
COLUMNA_FECHA_REQ = "Fecha ingreso, ascenso o traslado"
COLUMNA_FECHA_CIERRE = "Cierre proceso reclutamiento"

COLUMNAS_OBLIGATORIAS = [
    COLUMNA_REQUISICION,
    COLUMNA_PUESTO,
    COLUMNA_FECHA_REQ,
]


class AlertaValidacion:
    """Representa una alerta de validación con fila y columna."""

    def __init__(self, fila: int, columna: str, mensaje: str):
        self.fila = fila
        self.columna = columna
        self.mensaje = mensaje

    def __repr__(self):
        return f"AlertaValidacion(fila={self.fila}, columna='{self.columna}', mensaje='{self.mensaje}')"

    def to_dict(self):
        return {
            "fila": self.fila,
            "columna": self.columna,
            "mensaje": self.mensaje,
        }


def validar_fila(fila: dict, numero_fila: int) -> list[AlertaValidacion]:
    """Valida una fila del insumo y retorna una lista de alertas.

    Args:
        fila: Diccionario con los datos de una fila del Excel.
        numero_fila: Número de fila en el archivo original (para reportar en la alerta).

    Returns:
        Lista de AlertaValidacion (vacía si la fila es válida).
    """
    alertas: list[AlertaValidacion] = []

    # Validar campos obligatorios vacíos
    for columna in COLUMNAS_OBLIGATORIAS:
        valor = fila.get(columna)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            alertas.append(
                AlertaValidacion(
                    fila=numero_fila,
                    columna=columna,
                    mensaje=f"Campo obligatorio vacío: '{columna}'",
                )
            )

    # Validar fecha de requisición (debe ser datetime válido)
    fecha_req = fila.get(COLUMNA_FECHA_REQ)
    if fecha_req is not None and not isinstance(fecha_req, datetime):
        alertas.append(
            AlertaValidacion(
                fila=numero_fila,
                columna=COLUMNA_FECHA_REQ,
                mensaje=f"Fecha inválida en '{COLUMNA_FECHA_REQ}': se esperaba fecha, se recibió {type(fecha_req).__name__}",
            )
        )

    # Validar fecha de cierre (opcional, pero si está presente debe ser datetime válido)
    fecha_cierre = fila.get(COLUMNA_FECHA_CIERRE)
    if fecha_cierre is not None and not isinstance(fecha_cierre, datetime):
        alertas.append(
            AlertaValidacion(
                fila=numero_fila,
                columna=COLUMNA_FECHA_CIERRE,
                mensaje=f"Fecha inválida en '{COLUMNA_FECHA_CIERRE}': se esperaba fecha, se recibió {type(fecha_cierre).__name__}",
            )
        )

    return alertas


def validar_insumo(filas: list[dict], numero_fila_inicial: int = 2) -> list[AlertaValidacion]:
    """Valida todas las filas de un insumo y retorna todas las alertas encontradas.

    Args:
        filas: Lista de diccionarios con los datos de las filas del Excel.
        numero_fila_inicial: Número de fila donde empiezan los datos en el archivo original.

    Returns:
        Lista de AlertaValidacion con todas las alertas de todas las filas.
    """
    todas_alertas: list[AlertaValidacion] = []
    for idx, fila in enumerate(filas):
        numero_fila = numero_fila_inicial + idx
        alertas_fila = validar_fila(fila, numero_fila)
        todas_alertas.extend(alertas_fila)
    return todas_alertas


def validar_archivo_insumo(ruta_archivo: str | None = None) -> list[AlertaValidacion]:
    """Lee el insumo y valida todas sus filas.

    Args:
        ruta_archivo: Ruta opcional al archivo de insumos.

    Returns:
        Lista de AlertaValidacion con todas las alertas encontradas.
    """
    from app.services.lectura_insumos import leer_insumos

    filas = leer_insumos(ruta_archivo)
    return validar_insumo(filas)


if __name__ == "__main__":
    # Prueba con datos sintéticos para verificar la detección de errores
    filas_prueba = [
        # Fila válida
        {
            COLUMNA_REQUISICION: "REQ-001",
            COLUMNA_PUESTO: "Asistente",
            COLUMNA_FECHA_REQ: "01/03/2026",
        },
        # Fila con requisición vacía
        {
            COLUMNA_REQUISICION: "",
            COLUMNA_PUESTO: "Analista",
            COLUMNA_FECHA_REQ: "01/03/2026",
        },
        # Fila con puesto None
        {
            COLUMNA_REQUISICION: "REQ-003",
            COLUMNA_PUESTO: None,
            COLUMNA_FECHA_REQ: "01/03/2026",
        },
        # Fila con fecha de requisición inválida (texto)
        {
            COLUMNA_REQUISICION: "REQ-004",
            COLUMNA_PUESTO: "Contador",
            COLUMNA_FECHA_REQ: "TEXTO_INVALIDO",
        },
        # Fila completamente vacía en obligatorios
        {
            COLUMNA_REQUISICION: None,
            COLUMNA_PUESTO: None,
            COLUMNA_FECHA_REQ: None,
        },
    ]

    alertas = validar_insumo(filas_prueba, numero_fila_inicial=2)

    print(f"Se encontraron {len(alertas)} alertas:")
    for a in alertas:
        print(f"  Fila {a.fila}, Columna '{a.columna}': {a.mensaje}")

    # Verificaciones esperadas
    assert len(alertas) >= 5, f"Se esperaban al menos 5 alertas, se obtuvieron {len(alertas)}"

    # Verificar que la fila 2 (índice 1) tenga alerta de requisición vacía
    alertas_fila_3 = [a for a in alertas if a.fila == 3]
    assert any("vacío" in a.mensaje for a in alertas_fila_3), "Fila 3 debe tener alerta de campo vacío"

    print("Pruebas de R6 pasadas correctamente.")
