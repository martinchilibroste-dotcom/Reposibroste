# De un archivo único a una arquitectura modular

Comparación entre `15_agente_con_web_search.py` (monolítico) y la versión modularizada (`16_agente_modular.py` + `tools.py` + `agent_runner.py`).

---

## El problema del archivo único

En `15_agente_con_web_search.py` todo convive en un solo archivo:

```
15_agente_con_web_search.py
 ├── API keys
 ├── Función obtener_clima()
 ├── Función calcular_descuento()
 ├── Función buscar_en_web()
 ├── Lista tools (esquemas JSON)
 ├── Diccionario available_functions
 └── Loop main() con el cliente y el historial
```

Esto funciona bien cuando el agente tiene 2 o 3 herramientas. Pero a medida que crece, el archivo se vuelve difícil de leer, de mantener y de reutilizar.

---

## La solución: separar responsabilidades

La versión modular divide el código en tres archivos, cada uno con **una sola razón para cambiar**:

```
tools.py              → ¿qué puede hacer el agente?
agent_runner.py       → ¿cómo se orquesta la conversación?
16_agente_modular.py  → ¿cómo arranca y configura el agente?
```

### `tools.py` — Las herramientas

Contiene todo lo relacionado con las herramientas:

| Sección | Qué hay |
|---------|---------|
| **Funciones reales** | `obtener_clima()`, `calcular_descuento()`, `buscar_en_web()` |
| **`TOOLS_SCHEMAS`** | Lista de esquemas JSON que el LLM lee para decidir qué tool usar |
| **`AVAILABLE_FUNCTIONS`** | Diccionario `nombre → función` que el runner usa para ejecutar |

### `agent_runner.py` — El loop del agente

Contiene la lógica de las **dos llamadas al LLM**:

```
Llamada 1 → ¿el modelo quiere usar una tool?
    └── Sí → ejecutar la función → agregar resultado al historial
         └── Llamada 2 → el modelo genera la respuesta final
    └── No → usar la respuesta directamente
```

No importa `obtener_clima` ni ninguna otra función concreta.
Solo importa `TOOLS_SCHEMAS` y `AVAILABLE_FUNCTIONS` desde `tools.py`.

### `16_agente_modular.py` — El punto de entrada

Solo se ocupa de:
- Crear el cliente de la API.
- Inicializar el historial con el system prompt.
- Leer el input del usuario.
- Llamar a `run_agent()` de `agent_runner.py`.

---

## Comparación directa

| Aspecto | `15_agente_con_web_search.py` | Versión modular |
|---------|-------------------------------|-----------------|
| **Archivos** | 1 | 3 |
| **Líneas por archivo** | ~310 | ~50 / ~80 / ~160 |
| **Agregar una herramienta** | Editar el mismo archivo en 4 lugares | Solo editar `tools.py` en 3 lugares |
| **Reutilizar el runner** | Hay que copiar y pegar el loop | Importar `run_agent()` desde otro script |
| **Reutilizar las tools** | Ídem | Importar desde `tools.py` |
| **Testear una función** | Hay que importar el script entero | `from tools import obtener_clima` |

---

## Ventajas concretas

### 1. Agregar herramientas sin tocar el loop

En la versión monolítica, agregar `enviar_email()` implica editar `15_agente_con_web_search.py` y correr el riesgo de romper el loop. En la modular, solo se edita `tools.py`:

```python
# tools.py — los tres únicos lugares a modificar:

def enviar_email(destinatario, asunto, cuerpo):   # A) función
    ...

TOOLS_SCHEMAS = [
    ...
    { "type": "function", "function": { "name": "enviar_email", ... } }  # B) esquema
]

AVAILABLE_FUNCTIONS = {
    ...
    "enviar_email": enviar_email   # C) registro
}
```

`agent_runner.py` y `16_agente_modular.py` **no cambian**.

### 2. El runner es reutilizable

Si mañana querés un agente distinto (con otras herramientas o un system prompt diferente), podés crear `17_agente_ventas.py` que importe el mismo `run_agent()`:

```python
from agent_runner import run_agent
```

### 3. Fácil de testear

Podés probar una herramienta de forma aislada sin levantar el agente completo:

```python
from tools import buscar_en_web
print(buscar_en_web("precio del dólar hoy"))
```

---

## Qué tener en cuenta

### Las API keys siguen viviendo en el `.env`
`tools.py` llama a `load_dotenv()` y lee las keys con `os.getenv()`.
No hay que duplicar esto en el archivo principal.

### El historial `messages` se pasa por referencia
`run_agent()` recibe la lista `messages` y la **modifica en lugar** (`.append()`).
Esto es intencional: permite que el historial se acumule entre turnos sin retornar nada.

```python
# agent_runner.py
def run_agent(client, model, messages):   # messages se modifica aquí adentro
    ...
    messages.append(response_message)     # el cambio se ve afuera también
```

### `importlib.reload(config)` sigue en el punto de entrada
La recarga en caliente del config corresponde al archivo de arranque (`16_agente_modular.py`), no al runner. Así se puede cambiar el model o el system prompt sin reiniciar.

### Orden de imports entre módulos
```
16_agente_modular.py
  └── importa agent_runner.py
        └── importa tools.py
              └── importa os, json, requests, dotenv
```
No hay importaciones circulares porque la dependencia va en una sola dirección.

---

## Regla práctica para recordar

> **Para agregar una herramienta nueva: solo tocás `tools.py`.**
> Para cambiar cómo el agente conversa: solo tocás `agent_runner.py`.
> Para cambiar la configuración o el modelo: solo tocás `16_agente_modular.py`.
