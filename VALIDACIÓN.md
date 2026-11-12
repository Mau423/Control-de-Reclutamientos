# VALIDACIÓN.md — Resultado de pruebas vs. AGENTS.md

Fecha de validación: 04/11/2026  
Proyecto: ControlVacantes  
Total de pruebas: 34  
Pruebas aprobadas: 34  
Pruebas fallidas: 0  

---

## 1. CIFRAS DE CONTROL

| Prueba | Esperado | Obtenido | Estado | Diferencia |
|--------|----------|----------|--------|------------|
| Caso 2 (REQ-002) — Días Transcurridos | 14 días | 14 días | ✅ PASA | Ninguna |
| Caso 2 (REQ-002) — Meta Días | 10 días | 10 días | ✅ PASA | Ninguna |
| Caso 2 (REQ-002) — Días Exceso | 4 días | 4 días | ✅ PASA | Ninguna |
| Caso 2 (REQ-002) — Estado Semáforo | ROJA | Rojo | ✅ PASA | Ninguna |

**Causa probable de diferencias:** N/A (no hay diferencias)

---

## 2. REGLAS DE NEGOCIO (R1-R6)

| Regla | Prueba | Esperado | Obtenido | Estado |
|-------|--------|----------|----------|--------|
| R1 | Días Transcurridos 01/03/2026 → 15/03/2026 | 14 | 14 | ✅ PASA |
| R1 | Fecha Cierre vacía → usa fecha actual | datetime válido | datetime válido | ✅ PASA |
| R1 | Fecha Requisición None | None | None | ✅ PASA |
| R1 | Fecha Requisición texto inválido | None | None | ✅ PASA |
| R2 | Días Exceso = 14 - 10 | 4 | 4 | ✅ PASA |
| R2 | Días Transcurridos None | None | None | ✅ PASA |
| R2 | Días Transcurridos < Meta (5 - 10) | -5 | -5 | ✅ PASA |
| R3 | 10 días (igual a meta) | Verde | Verde | ✅ PASA |
| R3 | 5 días (menor a meta) | Verde | Verde | ✅ PASA |
| R3 | 11 días (meta + 1) | Amarillo | Amarillo | ✅ PASA |
| R3 | 12 días (meta + 2) | Amarillo | Amarillo | ✅ PASA |
| R3 | 13 días (meta + 3) | Rojo | Rojo | ✅ PASA |
| R3 | None | None | None | ✅ PASA |
| R4 | Filtrar por ejecutor "Ana" | 2 filas | 2 filas | ✅ PASA |
| R4 | Filtro None | todas las filas | todas las filas | ✅ PASA |
| R4 | Filtro string vacío | todas las filas | todas las filas | ✅ PASA |
| R4 | Ejecutores únicos | lista ordenada | lista ordenada | ✅ PASA |
| R6 | Fila válida | 0 alertas | 0 alertas | ✅ PASA |
| R6 | Requisición vacía | ≥1 alerta con columna | ≥1 alerta con columna | ✅ PASA |
| R6 | Puesto None | ≥1 alerta con columna "Puesto" | ≥1 alerta con columna "Puesto" | ✅ PASA |
| R6 | Fecha Requisición texto inválido | ≥1 alerta con columna "Fecha ingreso..." | ≥1 alerta con columna "Fecha ingreso..." | ✅ PASA |
| R6 | Alerta tiene fila y columna | fila=10, columna≠None | fila=10, columna≠None | ✅ PASA |

**Causa probable de diferencias:** N/A (no hay diferencias)

---

## 3. CASOS LÍMITE

| Caso límite | Esperado | Obtenido | Estado | Causa probable de diferencia |
|-------------|----------|----------|--------|------------------------------|
| Archivo vacío | 0 filas, 0 alertas | 0 filas, 0 alertas | ✅ PASA | N/A |
| Fecha Cierre vacía → fecha actual | ≥0 días | ≥0 días | ✅ PASA | N/A |
| Fecha Cierre None no es error | 0 alertas por cierre | 0 alertas por cierre | ✅ PASA | N/A |
| Dato corrupto (fecha requisición texto) | Alerta con fila y columna | Alerta con fila y columna | ✅ PASA | N/A |
| Dato corrupto (fecha cierre corrupta) | Alerta con fila y columna | Alerta con fila y columna | ✅ PASA | N/A |
| Columna Requisición faltante | Alerta con columna "Requisición..." | Alerta con columna "Requisición..." | ✅ PASA | N/A |
| Columnas obligatorias faltantes | 3 alertas | 3 alertas | ✅ PASA | N/A |
| Fecha como texto en R1 | None | None | ✅ PASA | N/A |

**Causa probable de diferencias:** N/A (no hay diferencias)

---

## 4. RESUMEN DE VALIDACIÓN

| Métrica | Valor |
|---------|-------|
| Total de pruebas | 34 |
| Pruebas aprobadas | 34 |
| Pruebas fallidas | 0 |
| Porcentaje de éxito | 100% |
| Diferencias encontradas | 0 |

**Conclusión:** Todas las reglas de negocio (R1-R6), las cifras de control (Caso 2: REQ-002) y los casos límite definidos en AGENTS.md se implementan correctamente. No hay diferencias entre el esperado y el obtenido.

---

## 5. ARCHIVOS DE PRUEBA

- `tests/test_reglas.py` — Pruebas de reglas R1-R6 y cifras de control
- `tests/test_casos_limite.py` — Pruebas de casos límite de AGENTS.md
- `tests/__init__.py` — Paquete de pruebas

**Comando para ejecutar:** `uv run pytest tests/ -v`
