"""Integración del agente de IA.

Lee la API Key de .env, filtra los campos sensibles antes de enviar al agente,
y devuelve una respuesta con el contrato JSON de 5 llaves.

Contrato de salida del agente:
  - id_requisicion: string
  - nivel_critico: string (Bajo, Medio, Alto)
  - resumen_ejecutivo: string
  - observaciones: string
  - accion_sugerida: string

Regla estricta: El agente nunca inventa datos. Si un dato no está presente,
debe escribir "no indicado".
"""

import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

IA_API_KEY = os.getenv("IA_API_KEY")

# Campos que se envían al agente (filtrados, sin datos sensibles)
CAMPOS_PARA_IA = [
    "id_requisicion",
    "puesto",
    "ejecutor",
    "dias_transcurridos",
    "meta_dias",
    "dias_exceso",
    "estado_semaforo",
]


def preparar_payload_ia(registro: dict) -> dict:
    """Prepara el payload filtrado que se enviará al agente de IA.

    Solo incluye los campos permitidos por el contrato de entrada del agente.
    No incluye datos sensibles (Salario, Nombre Candidato no existen en el insumo).

    Args:
        registro: Diccionario con los datos procesados de una fila.

    Returns:
        Diccionario filtrado con solo los campos para la IA.
    """
    return {campo: registro.get(campo) for campo in CAMPOS_PARA_IA}


def llamar_agente_ia(payload: dict) -> dict:
    """Envía el payload al agente de IA y retorna la respuesta con el contrato JSON.

    Esta función es un placeholder para la llamada real al modelo de IA.
    En producción, aquí se haría la petición HTTP usando IA_API_KEY desde .env.

    Args:
        payload: Diccionario filtrado con los campos para la IA.

    Returns:
        Diccionario con las 5 llaves del contrato:
          id_requisicion, nivel_critico, resumen_ejecutivo, observaciones, accion_sugerida.

    Raises:
        ValueError: Si IA_API_KEY no está configurada.
        RuntimeError: Si la respuesta del agente no es un JSON válido o no tiene las llaves requeridas.
    """
    if not IA_API_KEY:
        raise ValueError(
            "IA_API_KEY no está configurada. Cree un archivo .env con IA_API_KEY=su_clave"
        )

    # TODO: Aquí se haría la llamada real al modelo de IA usando IA_API_KEY.
    # Ejemplo:
    # import requests
    # headers = {"Authorization": f"Bearer {IA_API_KEY}", "Content-Type": "application/json"}
    # respuesta = requests.post(URL_IA, json=payload, headers=headers, timeout=30)
    # respuesta.raise_for_status()
    # datos = respuesta.json()

    # Modo simulado para pruebas: retorna una respuesta con el contrato esperado
    id_requisicion = payload.get("id_requisicion", "no indicado")
    dias_exceso = payload.get("dias_exceso")
    estado = payload.get("estado_semaforo", "")

    if dias_exceso is not None and dias_exceso > 0:
        nivel = "Alto" if estado == "Rojo" else "Medio"
    else:
        nivel = "Bajo"

    respuesta_simulada = {
        "id_requisicion": str(id_requisicion) if id_requisicion else "no indicado",
        "nivel_critico": nivel,
        "resumen_ejecutivo": f"Vacante {id_requisicion} con estado {estado.lower() if estado else 'no indicado'}",
        "observaciones": "Análisis cuantitativo de la desviación respecto a la meta establecida.",
        "accion_sugerida": "Recomendación operativa concreta para el reclutador a cargo.",
    }

    return validar_respuesta_ia(respuesta_simulada)


def validar_respuesta_ia(respuesta: dict) -> dict:
    """Valida que la respuesta del agente tenga las 5 llaves del contrato.

    Args:
        respuesta: Diccionario con la respuesta del agente.

    Returns:
        El mismo diccionario si es válido.

    Raises:
        RuntimeError: Si falta alguna llave requerida o el tipo no es correcto.
    """
    llaves_requeridas = [
        "id_requisicion",
        "nivel_critico",
        "resumen_ejecutivo",
        "observaciones",
        "accion_sugerida",
    ]

    for llave in llaves_requeridas:
        if llave not in respuesta:
            raise RuntimeError(
                f"La respuesta del agente no contiene la llave requerida: '{llave}'"
            )
        if not isinstance(respuesta[llave], str):
            raise RuntimeError(
                f"La llave '{llave}' debe ser string, se recibió {type(respuesta[llave]).__name__}"
            )

    return respuesta


def analizar_con_ia(registro: dict) -> dict:
    """Analiza un registro usando el agente de IA.

    Flujo completo: prepara el payload filtrado, llama al agente y valida la respuesta.

    Args:
        registro: Diccionario con los datos procesados de una fila.

    Returns:
        Diccionario con las 5 llaves del contrato JSON de salida del agente.

    Raises:
        ValueError: Si IA_API_KEY no está configurada.
        RuntimeError: Si la respuesta del agente no es válida.
    """
    payload = preparar_payload_ia(registro)
    return llamar_agente_ia(payload)


if __name__ == "__main__":
    # Prueba rápida con un registro de ejemplo
    registro_ejemplo = {
        "id_requisicion": "REQ-002",
        "puesto": "Desarrollador",
        "ejecutor": "Luis",
        "dias_transcurridos": 14,
        "meta_dias": 10,
        "dias_exceso": 4,
        "estado_semaforo": "Rojo",
    }

    print("Probando preparación de payload...")
    payload = preparar_payload_ia(registro_ejemplo)
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    print("\nProbando validación de respuesta...")
    respuesta = analizar_con_ia(registro_ejemplo)
    print(f"Respuesta IA: {json.dumps(respuesta, indent=2, ensure_ascii=False)}")

    # Validar contrato
    assert "id_requisicion" in respuesta
    assert "nivel_critico" in respuesta
    assert "resumen_ejecutivo" in respuesta
    assert "observaciones" in respuesta
    assert "accion_sugerida" in respuesta
    print("\nPruebas de integración IA pasadas correctamente.")
