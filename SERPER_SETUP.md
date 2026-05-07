# Cómo obtener y validar la API Key de Serper

Serper es un servicio que expone la búsqueda de Google como una API REST sencilla.
El plan gratuito incluye **2.500 búsquedas/mes**, más que suficiente para desarrollo y clases.

---

## Paso 1 — Crear una cuenta en Serper

1. Ingresá a [https://serper.dev](https://serper.dev)
2. Hacé clic en **Sign Up** (podés usar tu cuenta de Google).
3. Una vez dentro, vas a ver tu **Dashboard** principal.

---

## Paso 2 — Obtener la API Key

1. En el menú lateral izquierdo, hacé clic en **API Key**.
2. Tu clave ya está generada. Copiála con el botón **Copy**.

> La clave tiene este formato: `a3f92bc17e4d0c85f61a2e309b7d4c28ef105d37`

---

## Paso 3 — Guardar la key en el archivo `.env`

Abrí el archivo `.env` de tu proyecto y agregá esta línea:

```
SERPER_API_KEY=tu_clave_aqui
```

Ejemplo real:
```
SERPER_API_KEY=fcc10ad223b1a7f6db0cfbb89de25b6aaa96fa51
```

> **Nunca** pegues la API key directamente en el código Python.
> El archivo `.env` está (o debería estar) en el `.gitignore` para que no se suba a GitHub.

---

## Paso 4 — Validar que la key funciona

Antes de correr el agente, podés probar la API con este script mínimo.
Guardalo como `test_serper.py` y ejecutalo:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}
payload = {"q": "OpenAI últimas noticias", "num": 3, "hl": "es"}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    for i, item in enumerate(data.get("organic", []), 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}\n")
else:
    print(f"Error {response.status_code}: {response.text}")
```

Ejecutalo desde la terminal:

```bash
python test_serper.py
```

**Salida esperada** (si la key es válida):
```
1. OpenAI lanza GPT-5 con capacidades...
   https://...

2. Las últimas novedades de OpenAI en 2025...
   https://...
```

Si ves resultados, la key funciona correctamente y el agente está listo para usarse.

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `401 Unauthorized` | API key inválida o mal copiada | Verificá que no tenga espacios extra en el `.env` |
| `403 Forbidden` | Cuenta suspendida o límite superado | Revisá el dashboard en serper.dev |
| `SERPER_API_KEY no configurada` | La variable no se cargó del `.env` | Verificá que `load_dotenv()` esté antes de `os.getenv()` |
| `ConnectionError` | Sin acceso a internet | Verificá tu conexión de red |

---

## Referencia rápida de la API

| Campo | Valor |
|-------|-------|
| Endpoint | `POST https://google.serper.dev/search` |
| Header auth | `X-API-KEY: <tu_key>` |
| Parámetro `q` | Consulta de búsqueda |
| Parámetro `num` | Cantidad de resultados (máx. 100) |
| Parámetro `hl` | Idioma: `es` español, `en` inglés |
| Plan gratuito | 2.500 búsquedas/mes |

Documentación oficial: [https://serper.dev/api-reference](https://serper.dev/api-reference)
