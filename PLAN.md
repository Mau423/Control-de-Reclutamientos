# PLAN.md — Plan de entregas ControlVacantes

## 1. RESUMEN

Vamos a construir ControlVacantes, una app web interna de RRHH para auditar tiempos de cierre de vacantes de reclutamiento. Entra un archivo Excel (`Insumos reclutamiento\RECLUTAMIENTO.xlsx`, hoja "Total") con 960 filas y 15 columnas. El agente de IA recibe un JSON filtrado (ID Requisición, Puesto, Ejecutor, Días Transcurridos, Meta Días, Días Exceso, Estado Semáforo) y devuelve un análisis con 5 llaves (id_requisicion, nivel_critico, resumen_ejecutivo, observaciones, accion_sugerida). Sale una interfaz con carga de Excel, panel de alertas con contadores Verde/Amarillo/Rojo, tabla interactiva con semáforo, modal de análisis IA y exportación a Excel.

## 2. LO QUE ENCONTRÉ

**Contexto (`Contexto\Contexto_Mi_App.md`):** Contiene el documento completo con 4 tablas extraídas. Define las reglas R1-R6, el contrato JSON del agente, las cifras de control (Caso 2: 14 días, meta 10, exceso 4, ROJA), los casos límite y los supuestos S1-S3.

**Insumos (`Insumos reclutamiento\RECLUTAMIENTO.xlsx`):** 6 hojas. La hoja "Total" tiene 960 filas de datos y 15 columnas reales: #, Puesto, Tipo de Puesto, Número de plaza, Estadísticas, Razón de salida de colaborador a reemplazar, Cantidad entrevistas, Requisición de puesto, Cierre proceso reclutamiento, Cantidad días proceso reclutamiento, Fecha ingreso, ascenso o traslado, Ejecuta, Movimiento, Status, Ingreso.

**Coincidencia con AGENTS.md:** AGENTS.md ya refleja el mapeo acordado (Fecha Requisición = "Fecha ingreso, ascenso o traslado", Meta Días = 10 constante, Salario y Nombre Candidato eliminados porque no existen en el insumo, hoja "Total" como origen de datos). No hay contradicciones pendientes.

**Qué falta o no cuadra:** Nada pendiente. Todos los puntos abiertos fueron resueltos: se usa "Fecha ingreso, ascenso o traslado" como Fecha Requisición, Meta Días = 10 constante, se eliminan reglas de privacidad sobre Salario/Nombre Candidato, mapeo de "Requisición de puesto" y "Ejecuta", y hoja "Total" como la correcta.

## 3. ENTREGAS POR SUBAGENTE

Orden de ejecución: Backend → Frontend → Tester → Revisor.

### Fase Backend (@backend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| B1 | @backend | Estructura base del proyecto con uv: pyproject.toml, app/__init__.py con create_app(), wsgi.py, iniciar_app.bat, .env.example, .gitignore | pyproject.toml, app/__init__.py, wsgi.py, iniciar_app.bat, .env.example, .gitignore | — (inicio del proyecto) | Ejecutar `iniciar_app.bat` y ver que la app arranca sin errores en el navegador |
| B2 | @backend | Servicio de lectura de insumos: lee hoja "Total" de RECLUTAMIENTO.xlsx, devuelve filas con las 15 columnas | app/services/lectura_insumos.py | B1 (estructura base lista) | Ejecutar un script de prueba que imprima las primeras 3 filas leídas del Excel |
| B3 | @backend | Regla R1: cálculo de Días Transcurridos = Fecha Cierre - Fecha Requisición; si Fecha Cierre vacía, usa fecha actual | app/services/regla_r1.py | B2 (datos de entrada disponibles) | Ejecutar prueba unitaria: Caso 2 (REQ-002) debe dar 14 días transcurridos |
| B4 | @backend | Regla R2: cálculo de Días Exceso = Días Transcurridos - Meta Días (Meta = 10) | app/services/regla_r2.py | B3 (Días Transcurridos calculados) | Ejecutar prueba: Caso 2 debe dar Días Exceso = 4 |
| B5 | @backend | Regla R3: clasificación semáforo Verde/Amarillo/Rojo según umbrales | app/services/regla_r3.py | B4 (Días Exceso calculados) | Ejecutar prueba: Caso 2 debe mostrar estado ROJA |
| B6 | @backend | Regla R4: filtrado dinámico por columna Ejecutor (mapeada a "Ejecuta") | app/services/regla_r4.py | B5 (semáforo funcional) | Cargar el Excel y filtrar por un ejecutor, ver que solo aparecen sus filas |
| B7 | @backend | Regla R6: detección de fechas inválidas o campos obligatorios vacíos, con alerta de fila y columna | app/services/regla_r6.py | B6 (filtro por ejecutor) | Procesar un archivo con una fila inválida y ver la alerta específica |
| B8 | @backend | Controlador de carga y procesamiento: recibe el archivo, ejecuta reglas R1-R6, devuelve datos procesados | app/controllers/vacantes.py | B7 (todas las reglas de negocio listas) | Subir un Excel por la interfaz y ver el procesamiento sin errores |
| B9 | @backend | Integración agente de IA: lee llave de .env, filtra campos, envía JSON al agente, recibe respuesta con contrato de 5 llaves | app/services/agente_ia.py | B8 (datos procesados listos) | Ver en pantalla el JSON de respuesta del agente con las 5 llaves esperadas |
| B10 | @backend | Exportación a Excel de la tabla procesada con estados de alerta | app/services/exportacion.py | B9 (integración IA completa) | Click en "Exportar" y descargar un .xlsx con los datos y alertas |

### Fase Frontend (@frontend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| F1 | @frontend | Plantilla base.html: fondo oscuro, CSS embebido, navegación, bloques de contenido | app/templates/base.html | B1 (estructura Flask lista) | Abrir cualquier ruta de la app y ver el diseño base con fondo oscuro |
| F2 | @frontend | Pantalla de inicio: botón para adjuntar el archivo Excel de Control de Reclutamiento | app/templates/inicio.html | F1 (base.html lista) | Ir a la página de inicio y ver el botón de carga de Excel |
| F3 | @frontend | Pantalla de resultados: contadores grandes Verde/Amarillo/Rojo, tabla con semáforo, filtros por Ejecutor y nivel de alerta, botón "Ver Análisis IA", modal IA con JSON, botón Exportar | app/templates/resultados.html | B8 (controlador procesa datos) | Subir un Excel y ver la tabla completa con contadores, semáforos y filtros funcionando |

### Fase Tester (@tester)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| T1 | @tester | Pruebas en tests/ con pytest contra cifras de control y casos límite de AGENTS.md | tests/test_reglas.py, tests/test_casos_limite.py | B10 (backend completo) | Ejecutar `pytest` y ver que todas las pruebas pasan |
| T2 | @tester | VALIDACIÓN.md con esperado vs obtenido por cada prueba | VALIDACIÓN.md | T1 (pruebas escritas y ejecutadas) | Leer VALIDACIÓN.md y confirmar que no hay diferencias reportadas |

### Fase Revisor (@revisor)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| R1 | @revisor | Reporte de hallazgos: seguridad (llaves, datos sensibles, .gitignore) y cumplimiento de AGENTS.md, con prioridad y corrección propuesta | Reporte entregado al usuario (no modifica código) | T2 (VALIDACIÓN.md aprobado) | Leer el reporte de hallazgos y verificar que no haya problemas de prioridad Alta |

## 4. PUNTOS DE CONTROL

| Después de la entrega | Qué interviene @tester | Qué debe ver el usuario en pantalla |
|----------------------|------------------------|-------------------------------------|
| B3 (Regla R1) | Ejecuta prueba unitaria de Días Transcurridos | Caso 2 (REQ-002): 14 días transcurridos |
| B5 (Regla R3) | Ejecuta prueba de semáforo | Caso 2 (REQ-002): estado ROJA, exceso 4 días |
| B8 (Controlador) | Prueba de carga de archivo completo | App procesa el Excel y muestra resultados sin errores |
| B9 (Agente IA) | Prueba de contrato JSON | Modal muestra JSON con id_requisicion, nivel_critico, resumen_ejecutivo, observaciones, accion_sugerida |
| T1 (Pruebas pytest) | Ejecuta toda la suite | `pytest` reporta 0 errores, 0 fallos |
| R1 (Revisor) | No ejecuta pruebas, solo revisa | Reporte de hallazgos sin problemas de prioridad Alta |

## 5. RIESGOS

| Riesgo | Qué hará @backend | Qué hará @frontend | Qué hará @tester | Qué hará @revisor |
|--------|-------------------|--------------------|------------------|-------------------|
| Datos incompletos en el Excel | Detiene la fila con alerta específica (R6) y continúa con las demás | Muestra mensaje claro al usuario si el archivo está vacío o sin columnas obligatorias | Prueba con archivo vacío y con filas incompletas | Verifica que no se expongan datos parciales como si fueran completos |
| Archivo PDF escaneado (no aplica, solo .xlsx) | N/A | N/A | N/A | Verifica que solo se acepte .xlsx en la carga |
| Respuesta del agente que no es JSON válido | Captura el error y devuelve "no indicado" en los campos del JSON | Muestra mensaje de error en el modal si el JSON no llega | Prueba con respuesta malformada del agente | Verifica que no se exponga el error interno al usuario |
| Límite de la llave gratis del agente de IA | Lee la llave de .env y maneja cuota agotada con mensaje amable | Muestra aviso si el servicio IA no responde | Prueba que la app no se rompa si la IA falla | Verifica que la API Key nunca esté escrita en el código fuente |
| Columnas con nombres modificados en el Excel | Detecta columna faltante y muestra alerta específica (R6) | Muestra error de "Estructura inválida" en pantalla | Prueba con archivo que falte una columna obligatoria | Verifica que la validación de columnas esté en AGENTS.md |

## 6. PREGUNTAS PARA MÍ

Antes de comenzar, necesito confirmar lo siguiente:

1. **¿Deseo que proceda con este plan tal cual, o quiere ajustar alguna entrega?** (por ejemplo, agrupar reglas de negocio o cambiar el orden de entregas).
2. **¿Quiere que yo, como @arquitecto, asigne las entregas a los subagentes correspondientes (@backend, @frontend, @tester, @revisor) una vez usted apruebe este plan, o prefiere hacerlo usted mismo?**
3. **¿Hay alguna fecha límite o prioridad específica para alguna entrega en particular?**

Quedo a la espera de su aprobación para iniciar la construcción.