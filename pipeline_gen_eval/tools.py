"""
tools.py — Definición de todas las herramientas del agente.

Cada herramienta tiene DOS partes que deben vivir juntas aquí:
  1. La función Python que hace el trabajo real.
  2. El esquema JSON que le dice al LLM cómo y cuándo usarla.

Para agregar una nueva herramienta basta con:
  A) Definir la función.
  B) Agregar su esquema a TOOLS_SCHEMAS.
  C) Registrarla en AVAILABLE_FUNCTIONS.
  El archivo principal (agent_runner.py) no necesita ningún cambio.
"""

import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import markdown

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SERPER_API_KEY  = os.getenv("SERPER_API_KEY")


# ══════════════════════════════════════════════
# SECCIÓN 1 — FUNCIONES REALES
# ══════════════════════════════════════════════

def obtener_clima(ciudad: str) -> str:
    """Retorna el clima actual de una ciudad (OpenWeatherMap)."""
    if not WEATHER_API_KEY:
        return json.dumps({"error": "WEATHER_API_KEY no configurada en el archivo .env"})
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        )
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "ciudad":           data["name"],
                "pais":             data["sys"]["country"],
                "temperatura":      data["main"]["temp"],
                "sensacion_termica":data["main"]["feels_like"],
                "humedad":          data["main"]["humidity"],
                "descripcion":      data["weather"][0]["description"],
                "viento":           data["wind"]["speed"]
            }, ensure_ascii=False)
        return json.dumps({"error": f"Ciudad no encontrada (código: {response.status_code})"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def calcular_descuento(precio: float, porcentaje: float) -> str:
    """Devuelve el precio final luego de aplicar un porcentaje de descuento."""
    resultado = float(precio) * (1 - float(porcentaje) / 100)
    return json.dumps({"precio_final": round(resultado, 2)})


def buscar_en_web(consulta: str, num_resultados: int = 5) -> str:
    """Busca en Google usando Serper y devuelve los resultados orgánicos."""
    if not SERPER_API_KEY:
        return json.dumps({"error": "SERPER_API_KEY no configurada en el archivo .env"})
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": consulta, "num": num_resultados, "hl": "es"},
            timeout=10
        )
        if response.status_code == 200:
            items = response.json().get("organic", [])
            resultados = [
                {"titulo": i.get("title", ""), "enlace": i.get("link", ""), "fragmento": i.get("snippet", "")}
                for i in items
            ]
            return json.dumps({"consulta": consulta, "resultados": resultados}, ensure_ascii=False)
        return json.dumps({"error": f"Error Serper (código: {response.status_code}): {response.text}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def generar_informe_html(titulo: str, contenido: str, nombre_archivo: str = "") -> str:
    """
    Convierte el contenido Markdown a un archivo HTML y lo guarda en docs/.

    Ventajas sobre PDF:
      - No requiere dependencias externas (usa la librería estándar + markdown).
      - El Markdown se convierte directamente a HTML preservando toda la
        estructura: títulos, negrita, listas, bloques de código, etc.
      - Se puede abrir en cualquier navegador sin instalar nada.

    Args:
        titulo:         Título principal del informe (aparece en <h1> y <title>).
        contenido:      Cuerpo del informe en formato Markdown.
        nombre_archivo: Nombre del archivo sin extensión.
                        Si se omite, se genera automáticamente con timestamp.

    Returns:
        str: JSON con la ruta del archivo generado o un mensaje de error.
    """
    try:
        docs_dir = Path(__file__).parent / "docs"
        docs_dir.mkdir(exist_ok=True)

        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"informe_{timestamp}"

        ruta = docs_dir / f"{nombre_archivo}.html"

        # markdown.markdown() convierte el MD a HTML con extensiones comunes:
        # - fenced_code: bloques de código con triple backtick
        # - tables: tablas con sintaxis Markdown
        # - nl2br: saltos de línea simples → <br>
        cuerpo_html = markdown.markdown(
            contenido,
            extensions=["fenced_code", "tables", "nl2br"]
        )

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        # HTML completo con estilos inline — no requiere archivos externos
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 860px; margin: 40px auto; padding: 0 24px;
            color: #1a1a1a; line-height: 1.7; }}
    h1   {{ background: #1e1e1e; color: #fff; padding: 16px 20px;
            border-radius: 6px; font-size: 1.6em; }}
    h2   {{ color: #2c2c2c; border-bottom: 2px solid #e0e0e0; padding-bottom: 4px; }}
    h3   {{ color: #444; }}
    pre  {{ background: #f4f4f4; padding: 14px; border-radius: 6px;
            overflow-x: auto; font-size: 0.9em; }}
    code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px;
            font-size: 0.9em; }}
    pre code {{ background: none; padding: 0; }}
    blockquote {{ border-left: 4px solid #ccc; margin: 0; padding-left: 16px;
                  color: #555; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #f0f0f0; }}
    .meta {{ color: #888; font-size: 0.85em; margin-top: -8px; margin-bottom: 24px; }}
  </style>
</head>
<body>
  <h1>{titulo}</h1>
  <p class="meta">Generado el {fecha}</p>
  {cuerpo_html}
</body>
</html>"""

        ruta.write_text(html, encoding="utf-8")
        return json.dumps({"archivo": str(ruta), "estado": "Informe HTML generado exitosamente"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error al generar el informe: {str(e)}"})


# ══════════════════════════════════════════════
# SECCIÓN 2 — ESQUEMAS JSON (el "contrato" con el LLM)
#
# El LLM lee estos esquemas para saber:
#   - Qué herramientas tiene disponibles.
#   - Cuándo usarlas (description).
#   - Qué argumentos pasarles (parameters).
# ══════════════════════════════════════════════

TOOLS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene el clima actual de una ciudad. Úsala cuando el usuario pregunte por temperatura, clima o condiciones meteorológicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad (ej: 'Buenos Aires', 'Madrid')"
                    }
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_descuento",
            "description": "Calcula el precio final aplicando un porcentaje de descuento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "precio":     {"type": "number", "description": "Precio original del producto"},
                    "porcentaje": {"type": "number", "description": "Porcentaje de descuento a aplicar"}
                },
                "required": ["precio", "porcentaje"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_web",
            "description": (
                "Busca información actualizada en Google. Úsala para noticias recientes, "
                "eventos actuales o cualquier dato que pueda haber cambiado después del "
                "entrenamiento del modelo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "Consulta a buscar en Google (ej: 'últimas noticias sobre IA')"
                    },
                    "num_resultados": {
                        "type": "integer",
                        "description": "Cantidad de resultados (por defecto 5, máximo 10)",
                        "default": 5
                    }
                },
                "required": ["consulta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_informe_html",
            "description": (
                "Genera un informe en formato HTML y lo guarda en la carpeta docs/. "
                "Úsala cuando el usuario pida exportar, guardar o generar un informe o documento "
                "con el contenido de la respuesta."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Título principal del informe"
                    },
                    "contenido": {
                        "type": "string",
                        "description": "Cuerpo del informe en formato Markdown."
                    },
                    "nombre_archivo": {
                        "type": "string",
                        "description": "Nombre del archivo sin extensión (ej: 'informe_decoradores'). Si se omite, se genera con timestamp."
                    }
                },
                "required": ["titulo", "contenido"]
            }
        }
    }
]


# ══════════════════════════════════════════════
# SECCIÓN 3 — ROUTER DE FUNCIONES
#
# Diccionario nombre → función Python.
# El agente lo usa para ejecutar la función correcta
# cuando el LLM devuelve un tool_call.
# ══════════════════════════════════════════════

AVAILABLE_FUNCTIONS = {
    "obtener_clima":      obtener_clima,
    "calcular_descuento": calcular_descuento,
    "buscar_en_web":      buscar_en_web,
    "generar_informe_html": generar_informe_html,
}
