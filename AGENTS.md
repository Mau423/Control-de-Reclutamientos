# AGENTS.md

## Qué es esta app

ControlVacantes es una aplicación web interna para el departamento de Recursos Humanos. Su objetivo principal es auditar, monitorear y optimizar los tiempos de respuesta y cierre de las vacantes de reclutamiento.

Problema que resuelve: Actualmente, el seguimiento de vacantes implica revisiones manuales en hojas de cálculo, lo que genera cuellos de botella en la identificación de atrasos, falta de visibilidad en el rendimiento por reclutador y tiempo perdido en la redacción manual de reportes de estado.

Tiempo total por jornada (proceso manual actual): ~1 hora diaria.

---

## Datos de entrada

Archivo de insumos: `Insumos reclutamiento\RECLUTAMIENTO.xlsx` (hoja "Total")

El contexto acepta .xlsx o .csv, pero el insumo real disponible es solo `.xlsx`.

Hoja "Total" — 960 filas de datos, 15 columnas:

| Columna | Nombre real en el Excel |
|---------|-------------------------|
| 1 | # |
| 2 | Puesto |
| 3 | Tipo de Puesto |
| 4 | Número de plaza |
| 5 | Estadísticas |
| 6 | Razón de salida de colaborador a reemplazar |
| 7 | Cantidad entrevistas |
| 8 | Requisición de puesto |
| 9 | Cierre proceso reclutamiento |
| 10 | Cantidad días proceso reclutamiento |
| 11 | Fecha ingreso, ascenso o traslado |
| 12 | Ejecuta |
| 13 | Movimiento |
| 14 | Status |
| 15 | Ingreso |

Mapeo de columnas del contexto a los nombres reales del Excel:

| Contexto | Nombre real en Excel |
|----------|----------------------|
| ID Requisición | Requisición de puesto |
| Puesto | Puesto |
| Ejecutor | Ejecuta |
| Fecha Requisición | Fecha ingreso, ascenso o traslado (sustituto confirmado) |
| Fecha Cierre | Cierre proceso reclutamiento |
| Meta Días | 10 (valor constante, no existe como columna en el Excel) |
| Salario | No existe en el insumo (regla de privacidad eliminada) |
| Nombre Candidato | No existe en el insumo (regla de privacidad eliminada) |

Otras hojas del archivo (no se procesan como datos de entrada de vacantes): Hoja2 (vacía), Estadística, Tiempo Respuesta Reclutadores, Rotación, Hoja1.

---

## Reglas de negocio (código, sin IA)

R1: El código debe calcular Días Transcurridos = Fecha Cierre - Fecha Requisición. Si Fecha Cierre está vacía, utilizar la Fecha Actual del sistema.
  - Fecha Requisición se toma de la columna "Fecha ingreso, ascenso o traslado".
  - Fecha Cierre se toma de la columna "Cierre proceso reclutamiento".

R2: El código debe calcular Días Exceso = Días Transcurridos - Meta Días. Meta Días = 10 (valor constante).

R3: Clasificación del semáforo:
  - Verde: Días Transcurridos <= Meta Días.
  - Amarillo: Días Transcurridos > Meta Días y Días Transcurridos <= (Meta Días + 2).
  - Rojo: Días Transcurridos > (Meta Días + 2).

R4: Permitir filtrado dinámico por la columna Ejecutor (mapeada a "Ejecuta").

R5: Eliminada por confirmación del usuario. Las columnas Salario y Nombre Candidato no existen en el insumo, por lo que no aplica filtro de privacidad sobre ellas.

R6: Si una fila contiene fechas inválidas o campos obligatorios vacíos, el código debe registrar una alerta específica con el número de fila y columna correspondiente.

Supuestos del contexto (S1-S3):
  - S1: Se asume que el seguimiento operacional de este proceso se realiza con frecuencia diaria.
  - S2: Se asume que las fechas del Excel fuente vienen en formato estándar DD/MM/AAAA.
  - S3: Se asume que los días transcurridos se cuentan en días calendario (si se requiere cambio a días hábiles, deberá modificarse la regla R1).

---

## Lo que hace el agente de IA

Rol: Auditor Senior de Reclutamiento y Selección.

Qué recibe: Un objeto JSON filtrado únicamente con ID Requisición, Puesto, Ejecutor, Días Transcurridos, Meta Días, Días Exceso y el Estado Semáforo.

Regla estricta: El agente nunca inventa datos. Si un motivo de atraso o dato no está presente en la información del backend, debe escribir "no indicado".

Contrato JSON de salida (respuesta de la IA):

```json
{
  "id_requisicion": "string",
  "nivel_critico": "string",
  "resumen_ejecutivo": "string",
  "observaciones": "string",
  "accion_sugerida": "string"
}
```

Definición de llaves:
- `id_requisicion`: Identificador único de la vacante evaluada.
- `nivel_critico`: Nivel de urgencia (Bajo, Medio, Alto).
- `resumen_ejecutivo`: Síntesis concisa del estado del puesto y días de desfase.
- `observaciones`: Análisis cuantitativo de la desviación respecto a la meta establecida.
- `accion_sugerida`: Recomendación operativa concreta para el reclutador a cargo.

---

## Qué produce la app

- Interfaz de carga: Botón para adjuntar el archivo Excel de Control de Reclutamiento.
- Panel de Alertas (Banner Superior): Contadores globales de vacantes en Verde, Amarillo y Rojo.
- Filtros de Búsqueda: Selector desplegable por Ejecutor (Reclutador) y filtro por nivel de alerta.
- Tabla Interactiva:
  - Columna con indicador visual de Semáforo (Verde / Amarillo / Rojo).
  - Muestra de Requisición, Puesto, Ejecutor, Fechas y Días Transcurridos.
- Botón "Ver Análisis IA" por cada fila fuera de meta.
- Modal de Inteligencia Artificial: Ventana emergente que muestra el análisis redactado por el agente de IA (JSON formateado).
- Botón de Exportación: Opción para descargar la tabla procesada junto con los estados de alerta en formato .xlsx.

---

## Quién decide

Usuarios de la app: Reclutadores y Jefe de Atracción.

Tomador de decisión final: Jefe de Atracción (decide las reasignaciones de vacantes, ajustes de metas o acciones correctivas a tomar con base en los reportes).

---

## Cifras de control

Al procesar la prueba del Caso 2 (REQ-002):

- Fecha Inicio: 01/03/2026
- Fecha Cierre: 15/03/2026
- Días Transcurridos calculados: 14 días
- Meta: 10 días
- Resultado Esperado: 14 Días Transcurridos | Estado: Sobrepasado por 4 días | Alerta: ROJA.

---

## Casos límite

| Escenario | Comportamiento del Sistema |
|-----------|---------------------------|
| Archivo vacío | Muestra mensaje de error: "El archivo subido no contiene registros válidos." |
| Fecha de Cierre vacía | El sistema toma automáticamente la fecha actual para calcular los días transcurridos. |
| Dato corrupto o no válido | Interrumpe el procesamiento de esa fila y muestra alerta: "Error en Fila X, Columna 'Fecha Requisición': Formato no válido". |
| Columna con nombre modificado | Si falta una columna obligatoria, muestra: "Estructura inválida. Falta la columna: [Nombre Columna]". |

---

## Reglas del sistema

- Stack Tecnológico: Lenguaje Python con el framework Flask, siguiendo la arquitectura MVC (Modelo-Vista-Controlador).
- Gestión de Entorno: Administrado obligatoriamente mediante uv.
- Seguridad de credenciales: La API Key del agente de IA debe estar resguardada exclusivamente en el archivo .env y nunca expuesta en el código fuente.
- Ejecución: Incluir un script ejecutable `iniciar_app.bat` para iniciar el entorno virtual y el servidor web con un solo clic.
- Idioma e Interfaz: Pantallas limpias, intuitivas y 100% en español.
- Restricción de alcance: Queda estrictamente prohibido inventar reglas de negocio, métricas o campos que no estén detallados en este documento.

---

## Supuestos por confirmar (del contexto)

- S1: Se asume que el seguimiento operacional de este proceso se realiza con frecuencia diaria.
- S2: Se asume que las fechas del Excel fuente vienen en formato estándar DD/MM/AAAA.
- S3: Se asume que los días transcurridos se cuentan en días calendario (si se requiere cambio a días hábiles, deberá modificarse la regla R1).
