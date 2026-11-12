DOCUMENTO DE CONTEXTO · ControlVacantes

1. Qué es esta app

ControlVacantes es una aplicación web interna para el departamento de Recursos Humanos. Su objetivo principal es auditar, monitorear y optimizar los tiempos de respuesta y cierre de las vacantes de reclutamiento.

Problema que resuelve

Actualmente, el seguimiento de vacantes implica revisiones manuales en hojas de cálculo, lo que genera cuellos de botella en la identificación de atrasos, falta de visibilidad en el rendimiento por reclutador y tiempo perdido en la redacción manual de reportes de estado.

2. El proceso hoy


### Tabla 1

| Paso | Descripción | Responsable | Tiempo estimado |
| --- | --- | --- | --- |
| 1. Extracción | Descarga del archivo Excel de Control de Reclutamiento desde el sistema base. | Jefe de Atracción / Reclutador | 10 min |
| 2. Revisión | Verificación manual de fechas de requisición, fechas de cierre y cálculo de días transcurridos. | Jefe de Atracción | 20 min |
| 3. Filtrado | Separación manual de vacantes por reclutador a cargo para evaluar cargas de trabajo y retrasos. | Jefe de Atracción | 15 min |
| 4. Redacción | Elaboración de observaciones e informes de vacantes que superan el tiempo límite permitido. | Jefe de Atracción | 15 min |

Tiempo total por jornada: ~1 hora diaria.

3. Datos de entrada


### Tabla 2

| Archivo / Dato | Formato | Campos requeridos | Ejemplo |
| --- | --- | --- | --- |
| Control de Reclutamiento | .xlsx / .csv | ID Requisición | REQ-2026-089 |
|  |  | Puesto | Analista Contable |
|  |  | Ejecutor | Maria Perez |
|  |  | Fecha Requisición | 01/03/2026 |
|  |  | Fecha Cierre | 15/03/2026 (o vacío si sigue abierta) |
|  |  | Meta Días | 10 |
|  |  | Salario | $1,500 (Dato sensible local) |
|  |  | Nombre Candidato | Juan Gómez (Dato sensible local) |

4. Reglas de negocio para el código

R1: El código debe calcular Días Transcurridos = Fecha Cierre - Fecha Requisición. Si Fecha Cierre está vacía, utilizar la Fecha Actual del sistema.

R2: El código debe calcular Días Exceso = Días Transcurridos - Meta Días.

R3: Clasificación del semáforo:

Verde: Días Transcurridos <= Meta Días.

Amarillo: Días Transcurridos > Meta Días y Días Transcurridos <= (Meta Días + 2).

Rojo: Días Transcurridos > (Meta Días + 2).

R4: Permitir filtrado dinámico por la columna Ejecutor (Reclutador).

R5: Filtro de Privacidad: El código en Backend debe omitir/ocultar las columnas de Salario y Nombre Candidato antes de realizar cualquier envío de datos al Agente de IA.

R6: Si una fila contiene fechas inválidas o campos obligatorios vacíos, el código debe registrar una alerta específica con el número de fila y columna correspondiente.

5. Lo que hace el agente de IA

Rol

Auditor Senior de Reclutamiento y Selección.

Qué recibe

Un objeto JSON filtrado únicamente con el ID Requisición, Puesto, Ejecutor, Días Transcurridos, Meta Días, Días Exceso y el Estado Semáforo.

Regla estricta

El agente nunca inventa datos. Si un motivo de atraso o dato no está presente en la información del backend, debe escribir "no indicado".

Contrato JSON de Salida (Respuesta de la IA)


### Tabla 3

| Llave | Tipo | Definición |
| --- | --- | --- |
| id_requisicion | string | Identificador único de la vacante evaluada. |
| nivel_critico | string | Nivel de urgencia (Bajo, Medio, Alto). |
| resumen_ejecutivo | string | Síntesis concisa del estado del puesto y días de desfase. |
| observaciones | string | Análisis cuantitativo de la desviación respecto a la meta establecida. |
| accion_sugerida | string | Recomendación operativa concreta para el reclutador a cargo. |

6. Qué produce la app

Interfaz de carga: Botón para adjuntar el archivo Excel de Control de Reclutamiento.

Panel de Alertas (Banner Superior): Contadores globales de vacantes en Verde, Amarillo y Rojo.

Filtros de Búsqueda: Selector desplegable por Ejecutor (Reclutador) y filtro por nivel de alerta.

Tabla Interactiva:

Columna con indicador visual de Semáforo (Verde / Amarillo / Rojo).

Muestra de Requisición, Puesto, Ejecutor, Fechas y Días Transcurridos.

Botón "Ver Análisis IA" por cada fila fuera de meta.

Modal de Inteligencia Artificial: Ventana emergente que muestra el análisis redactado por el agente de IA (JSON formateado).

Botón de Exportación: Opción para descargar la tabla procesada junto con los estados de alerta en formato .xlsx.

7. Quién decide

Usuarios de la app: Reclutadores y Jefe de Atracción.

Tomador de decisión final: Jefe de Atracción (decide las reasignaciones de vacantes, ajustes de metas o acciones correctivas a tomar con base en los reportes).

8. Datos de prueba que hay que generar

Se debe crear un archivo prueba_vacantes.xlsx con los siguientes 3 registros ficticios:

Caso 1 (Verde): REQ-001 | Puesto: Asistente | Ejecutor: Ana | Fecha Req: 01/03/2026 | Fecha Cierre: 08/03/2026 | Meta: 10 días | Salario: $800 | Candidato: Carlos Ruiz

Caso 2 (Rojo): REQ-002 | Puesto: Desarrollador | Ejecutor: Luis | Fecha Req: 01/03/2026 | Fecha Cierre: 15/03/2026 | Meta: 10 días | Salario: $2,500 | Candidato: María López

Caso 3 (Error): REQ-003 | Puesto: Contador | Ejecutor: Ana | Fecha Req: TEXTO_INVALIDO | Fecha Cierre: 10/03/2026 | Meta: 10 días | Salario: $1,200 | Candidato: Pedro Gómez

9. Cifras de control

Al procesar la prueba del Caso 2 (REQ-002):

Fecha Inicio: 01/03/2026

Fecha Cierre: 15/03/2026

Días Transcurridos calculados: 14 días

Meta: 10 días

Resultado Esperado: 14 Días Transcurridos | Estado: Sobrepasado por 4 días | Alerta: ROJA.

10. Casos límite


### Tabla 4

| Escenario | Comportamiento del Sistema |
| --- | --- |
| Archivo vacío | Muestra mensaje de error: "El archivo subido no contiene registros válidos." |
| Fecha de Cierre vacía | El sistema toma automáticamente la fecha actual para calcular los días transcurridos. |
| Dato corrupto o no válido | Interrumpe el procesamiento de esa fila y muestra alerta: "Error en Fila X, Columna 'Fecha Requisición': Formato no válido". |
| Columna con nombre modificado | Si falta una columna obligatoria, muestra: "Estructura inválida. Falta la columna: [Nombre Columna]". |
| Datos sensibles | Las columnas Salario y Nombre Candidato deben ser completamente excluidas del payload que recibe el modelo de IA. |

11. Reglas del sistema

Stack Tecnológico: Lenguaje Python con el framework Flask, siguiendo la arquitectura MVC (Modelo-Vista-Controlador).

Gestión de Entorno: Administrado obligatoriamente mediante uv.

Seguridad de credenciales: La API Key del agente de IA debe estar resguardada exclusivamente en el archivo .env y nunca expuesta en el código fuente.

Ejecución: Incluir un script ejecutable iniciar_app.bat para iniciar el entorno virtual y el servidor web con un solo clic.

Idioma e Interfaz: Pantallas limpias, intuitivas y 100% en español.

Restricción de alcance: Queda estrictamente prohibido inventar reglas de negocio, métricas o campos que no estén detallados en este documento.

12. Supuestos por confirmar

S1: Se asume que el seguimiento operacional de este proceso se realiza con frecuencia diaria.

S2: Se asume que las fechas del Excel fuente vienen en formato estándar DD/MM/AAAA.

S3: Se asume que los días transcurridos se cuentan en días calendario (si se requiere cambio a días hábiles, deberá modificarse la regla R1).
