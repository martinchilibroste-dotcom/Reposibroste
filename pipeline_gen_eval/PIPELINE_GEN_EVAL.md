# Pipeline Generador → Evaluador → Optimizador

`17_generator_evaluator_pipeline.py` implementa un patrón donde **dos modelos colaboran con roles distintos** para producir respuestas de mayor calidad que cualquiera de ellos por separado.

---

## El problema que resuelve

En el agente modular (`16_agente_modular.py`), el modelo genera una respuesta y la entrega directamente al usuario. No hay ningún mecanismo que valide si esa respuesta es correcta, completa o tiene el tono adecuado. Si el modelo alucinó un dato o fue vago, el usuario lo recibe igual.

Este pipeline introduce una **capa de control de calidad automática** entre la generación y la entrega.

---

## Arquitectura: dos modelos, dos roles

```
                     consulta
                        │
                        ▼
          ┌─────────────────────────┐
          │       GENERADOR         │
          │   llama-3.1-8b-instant  │  ← rápido, usa herramientas
          └─────────────────────────┘
                        │
                   respuesta
                        │
                        ▼
          ┌─────────────────────────┐
          │       EVALUADOR         │
          │ llama-3.3-70b-versatile │  ← preciso, devuelve JSON
          └─────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
        aprobado                 rechazado
           │                         │
           ▼                         ▼
   respuesta al usuario     feedback → nueva consulta
                                      (hasta 5 intentos)
```

### El Generador — `llama-3.1-8b-instant`
- Produce la respuesta inicial.
- Puede usar herramientas reales: `obtener_clima`, `calcular_descuento`, `buscar_en_web`, `generar_informe_html`.
- Si el evaluador rechaza su respuesta, recibe el feedback y lo intenta de nuevo.
- Se eligió el modelo **8b** porque es rápido y barato: ideal para iterar varias veces.

### El Evaluador — `llama-3.3-70b-versatile`
- Audita la respuesta contra tres criterios: corrección técnica, completitud y tono.
- Devuelve siempre un **JSON estructurado** con `aprobado`, `puntaje`, `feedback` y `sugerencia`.
- Usa `temperature=0` (determinista) y `response_format={"type": "json_object"}` (JSON garantizado).
- Se eligió el modelo **70b** porque es más preciso: actúa como supervisor sin que su costo se multiplique por cada iteración.

---

## El ciclo de optimización

```
Intento 1
  ├── Generador produce respuesta A
  ├── Evaluador: rechazado (puntaje 6/10)
  │   feedback: "faltó explicar el concepto de closure"
  │   sugerencia: "agregá un ejemplo con funciones anidadas"
  └── La consulta del intento 2 incluye ese feedback

Intento 2
  ├── Generador produce respuesta B (corrigiendo el feedback)
  ├── Evaluador: aprobado (puntaje 9/10)
  └── Se muestra respuesta B al usuario ✅
```

El feedback del evaluador **no se descarta**: se convierte en la instrucción del siguiente intento. Esto es el corazón del patrón Optimizador.

---

## Comparación con el agente anterior

| Aspecto | `16_agente_modular.py` | `17_generator_evaluator_pipeline.py` |
|---------|------------------------|--------------------------------------|
| **Modelos** | 1 (70b para todo) | 2 (8b genera, 70b evalúa) |
| **Validación** | Ninguna | Automática, con criterios explícitos |
| **Reintentos** | No | Hasta 5, con feedback incorporado |
| **Salida** | Primera respuesta generada | Respuesta aprobada por el auditor |
| **Transparencia** | No muestra razonamiento interno | Muestra puntaje, feedback y sugerencias |
| **Costo por turno** | 1 llamada al 70b (o 2 si hay tools) | 1-2 llamadas al 8b + 1 al 70b por intento |
| **Exportación** | No | Informe HTML generado en `docs/` |

---

## Exportación de informe HTML

Después de mostrar la respuesta final, el pipeline ofrece generar un informe HTML en la carpeta `docs/`.

La pregunta es **abierta** — el usuario responde en lenguaje natural y un tercer LLM interpreta la intención:

```
📄 ¿Querés que genere un informe HTML con esta respuesta? dale, llamalo evolucion_python
   🤖 Perfecto, lo guardo como evolucion_python.html
   Generando informe HTML...
   ✅ Informe HTML guardado en: .../docs/evolucion_python.html
```

El LLM interpreta correctamente todas estas variantes:
- `"sí"` / `"dale"` / `"generalo"` → genera con nombre sugerido automáticamente
- `"sí, llamalo resumen_clase4"` → genera con ese nombre
- `"no"` / `"no gracias"` / `"después"` → no genera nada

Esto ilustra cómo reemplazar lógica de parseo frágil (`if input == "s"`) con comprensión semántica real usando JSON mode + `temperature=0`.

El HTML resultante incluye estilos CSS inline, renderiza el Markdown completo (títulos, listas, bloques de código, tablas) y se puede abrir en cualquier navegador sin instalar nada adicional.

---

## Conceptos técnicos clave

### JSON mode
```python
response_format={"type": "json_object"}
```
Fuerza al modelo a devolver **únicamente JSON válido**. Sin esto, el modelo puede agregar texto antes o después del objeto (`"Aquí está mi evaluación: {...}"`), lo que rompe `json.loads()`.

### temperature=0 en el evaluador
```python
temperature=0
```
El juicio del auditor debe ser **reproducible y consistente**, no creativo. Con temperatura 0, el mismo input siempre produce el mismo veredicto.

### run_agent_silent()
A diferencia del runner interactivo, esta función **retorna la respuesta** en lugar de imprimirla directamente. Eso permite que el pipeline la capture y se la entregue al evaluador antes de mostrarla al usuario.

### Guardar la mejor respuesta
```python
if puntaje > mejor_puntaje:
    mejor_respuesta = respuesta
```
Si se agotan los intentos sin aprobar, el pipeline no falla silenciosamente: muestra la respuesta con el **puntaje más alto** alcanzado.

---

## Cómo ejecutarlo

Desde la carpeta `pipeline_gen_eval/`:

```bash
python 17_generator_evaluator_pipeline.py
```

Ingresá cualquier consulta. Si la dejás vacía, usa una consulta de ejemplo sobre decoradores en Python.

**Salida esperada:**
```
🚀 INTENTO 1 de 5
   ⚙️  [GENERADOR] Usando llama-3.1-8b-instant...
   🔍 [EVALUADOR] Auditando con llama-3.3-70b-versatile...

✅ [CONTROL DE CALIDAD] APROBADO — Puntaje: 9/10

🤖 RESPUESTA FINAL APROBADA:
═══════════════════════════════════════════════════════
...

📄 ¿Querés que genere un informe HTML con esta respuesta? sí
   🤖 Perfecto, lo guardo como informe_20250430_160000.html
   Generando informe HTML...
   ✅ Informe HTML guardado en: .../docs/informe_20250430_160000.html
```

---

## Archivos del pipeline

```
pipeline_gen_eval/
 ├── tools.py                          ← herramientas del Generador (incluye generar_informe_html)
 ├── config2.py                        ← modelos + prompts (Generador, Evaluador, Asistente HTML)
 ├── agent_runner2.py                  ← run_agent_silent() (retorna respuesta sin imprimir)
 ├── 17_generator_evaluator_pipeline.py  ← pipeline principal
 ├── PIPELINE_GEN_EVAL.md              ← este documento
 └── docs/                             ← informes HTML generados (se crea automáticamente)
```

> La carpeta es **autocontenida**: tiene su propia copia de `tools.py` y no depende de archivos del directorio padre. Se puede copiar y ejecutar de forma independiente.
