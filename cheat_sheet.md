# Python para Ingeniería de Agentes: Cheat Sheet

Del Código Básico a la Orquestación de LLMs

---

## 1. Configuración y Seguridad

Nunca pongas tus API Keys directamente en el código. Usamos variables de entorno para que nuestro proyecto sea profesional y seguro.

**Instalación:**
```bash
pip install python-dotenv
```

**Archivo `.env`:**
```
OPENAI_API_KEY=sk-proj-xxxx...
MODEL_NAME=gpt-4o-mini
```

**Carga en Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

---

## 2. La Estructura de "Memoria"

Un LLM no recuerda nada por sí solo. Nosotros gestionamos el estado usando una lista de diccionarios.

**Esquema de Mensajes:**
```python
historial = [
    {"role": "system", "content": "Sos un experto en Python de Ramos Mejía."},
    {"role": "user", "content": "Hola, ¿cómo va?"},
    {"role": "assistant", "content": "Todo joya, ¿en qué te ayudo?"}
]
```

**Tip Pro:** Para agregar un nuevo mensaje:
```python
historial.append({"role": "user", "content": nuevo_input})
```

---

## 3. Manejo de Datos Estructurados (JSON)

Los agentes no solo escriben poemas; generan datos. Necesitás transformar strings en diccionarios de Python.

**De String a Diccionario:**
```python
import json

respuesta_ia = '{"nombre": "Agent 001", "status": "activo"}'
data = json.loads(respuesta_ia)
print(data["nombre"])  # Salida: Agent 001
```

**Validación con Pydantic (Nivel Profesional):**

Usa Pydantic para asegurar que la IA te envíe exactamente lo que pediste.

```python
from pydantic import BaseModel

class RespuestaAgente(BaseModel):
    plan: str
    herramienta_a_usar: str
    prioridad: int
```

---

## 4. Control de Errores y Flujo

Las APIs fallan (timeout, límites de velocidad, etc.). No dejes que tu script muera.

**El bloque de seguridad:**
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    print(f"Error en la API: {e}")
    # Aquí podrías implementar un reintento (retry)
```

---

## 5. Utilidades Rápidas

| Tarea | Fragmento de Código |
|-------|---------------------|
| Recortar historial | `historial = historial[-10:]` (mantiene solo los últimos 10 mensajes) |
| Limpiar texto | `texto.strip().lower()` (vital para comparar comandos) |
| Listar herramientas | `tools = [{"type": "function", "function": {...}}]` |

---

## 💡 Un consejo

> **"En el desarrollo de agentes, Python es el pegamento, no el cerebro. Tu trabajo es escribir pegamento que no se rompa cuando el cerebro (la IA) diga algo inesperado."**
