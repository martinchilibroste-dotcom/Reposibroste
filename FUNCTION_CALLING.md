# Function Calling: esquemas JSON y herramientas en agentes IA

## 1. El problema que resuelve

Un LLM por defecto solo produce **texto libre**. Si le preguntás "¿qué clima hace en Madrid?", puede inventar una respuesta o decir que no tiene acceso a datos en tiempo real. En ambos casos, el resultado es inútil para una aplicación real.

**Function Calling** (o Tool Use) es el mecanismo por el cual el modelo puede **pausar su respuesta**, solicitar la ejecución de una función externa, recibir el resultado real, y recién entonces formular su respuesta final. El modelo pasa de ser un generador de texto a ser un **orquestador de acciones**.

---

## 2. El contrato: JSON Schema

Para que el modelo sepa qué herramientas tiene disponibles y cómo usarlas, se le entrega un **contrato en JSON Schema**. Este contrato describe:

- El **nombre** de la función
- Una **descripción** en lenguaje natural (el modelo la usa para decidir cuándo llamarla)
- Los **parámetros** que acepta, con sus tipos y cuáles son obligatorios

### Ejemplo de contrato para `obtener_clima`

```json
{
  "type": "function",
  "function": {
    "name": "obtener_clima",
    "description": "Obtiene el clima actual de una ciudad específica. Usa esta función cuando el usuario pregunte por el clima, temperatura o condiciones meteorológicas.",
    "parameters": {
      "type": "object",
      "properties": {
        "ciudad": {
          "type": "string",
          "description": "El nombre de la ciudad (ej: 'Buenos Aires', 'Madrid', 'New York')"
        }
      },
      "required": ["ciudad"]
    }
  }
}
```

### Ejemplo de contrato para `calcular_descuento`

```json
{
  "type": "function",
  "function": {
    "name": "calcular_descuento",
    "description": "Calcula el precio final de un producto aplicando un porcentaje de descuento.",
    "parameters": {
      "type": "object",
      "properties": {
        "precio": {
          "type": "number",
          "description": "Precio original del producto."
        },
        "porcentaje": {
          "type": "number",
          "description": "Porcentaje de descuento a aplicar (ej: 15 para 15%)."
        }
      },
      "required": ["precio", "porcentaje"]
    }
  }
}
```

> **Clave**: la `description` de la función y de cada parámetro no es decorativa. El modelo la lee para razonar cuándo y cómo llamar a la herramienta. Una descripción vaga produce llamadas incorrectas o ausentes.

---

## 3. El flujo completo: dos llamadas a la API

El ciclo de function calling requiere **dos llamadas** al modelo:

```
Usuario
  │
  ▼
[LLAMADA 1] ──► Modelo analiza el mensaje + los contratos JSON
                       │
              ¿Necesita una tool?
                /            \
              SÍ              NO
              │                │
    Devuelve tool_calls    Devuelve respuesta
    con nombre + args      directamente (fin)
              │
              ▼
    Tu código ejecuta la función real
    (API externa, base de datos, cálculo...)
              │
              ▼
    Inyectás el resultado al historial
    con role: "tool" + tool_call_id
              │
              ▼
[LLAMADA 2] ──► Modelo ahora tiene el dato real
                       │
                       ▼
              Genera la respuesta final
```

### Por qué es importante el `tool_call_id`

Cuando el modelo hace múltiples llamadas a herramientas en paralelo, el `tool_call_id` es el **identificador que vincula cada resultado con la solicitud que lo originó**. Sin él, el modelo no puede saber qué resultado corresponde a qué función. La API rechaza el mensaje si falta.

```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,   # Vincula resultado con solicitud
    "name": function_name,
    "content": resultado_json,       # Siempre string, no dict
})
```

---

## 4. Entradas y salidas: por qué siempre strings JSON

### Entrada al modelo (los contratos)
Los parámetros se definen con tipos JSON estándar: `"string"`, `"number"`, `"boolean"`, `"array"`, `"object"`. El modelo usa estos tipos para extraer y formatear los argumentos correctamente desde el texto del usuario.

### Salida de las funciones (los resultados)
Los resultados que se inyectan al historial **siempre deben ser strings**. Si tu función devuelve un `dict` o cualquier otro tipo, hay que serializarlo con `json.dumps()` antes de agregarlo al mensaje.

```python
# ✅ Correcto
return json.dumps({"temperatura": 22, "descripcion": "soleado"})

# ❌ Incorrecto — la API espera string, no dict
return {"temperatura": 22, "descripcion": "soleado"}
```

Entregar un `dict` directamente produce un error o un doble-encoding que el modelo interpreta mal.

---

## 5. ¿Por qué es importante usar Function Tools en lugar de ReAct manual?

El ejemplo 13 (`13_ejecutar_tools.py`) implementa el ciclo Thought→Action→Observation parseando texto libre con regex. El ejemplo 14 (`14_agente_pro.py`) usa Function Calling nativo. La diferencia es significativa:

| | ReAct manual (ej. 13) | Function Calling nativo (ej. 14) |
|---|---|---|
| **Parsing** | Regex frágil sobre texto libre | Estructurado y garantizado por la API |
| **Argumentos** | El modelo puede inventar formato | JSON Schema valida tipos y campos |
| **Múltiples tools** | Secuencial, un turno por vez | El modelo puede pedir varias en paralelo |
| **Errores** | Silenciosos (texto mal parseado) | Explícitos (la API rechaza el mensaje) |
| **Confiabilidad** | Depende del modelo y del prompt | Contrato formal, independiente del modelo |
| **Mantenimiento** | Hay que mantener el parser | Solo mantener el JSON Schema |

Function Calling no es una feature opcional: es la forma **correcta y robusta** de conectar LLMs con el mundo real en producción.
