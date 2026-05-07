import os
import json
import importlib
import requests
from dotenv import load_dotenv
from openai import OpenAI
import config

load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ============================================================
# PASO 1: Leer la nueva API key desde el .env
# Siempre que agregues una herramienta que llama a una API
# externa, cargá su key aquí. Nunca la hardcodees en el código.
# ============================================================
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


# ─────────────────────────────────────────────
# FUNCIONES REALES (lo que el agente puede hacer)
# ─────────────────────────────────────────────

def obtener_clima(ciudad: str) -> str:
    """
    Obtiene el clima actual de una ciudad usando OpenWeatherMap API.
    
    Args:
        ciudad: Nombre de la ciudad (ej: "Buenos Aires", "Madrid")
    
    Returns:
        str: Información del clima en formato JSON
    """
    if not WEATHER_API_KEY:
        return json.dumps({"error": "WEATHER_API_KEY no configurada en el archivo .env"})
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            resultado = {
                "ciudad": data["name"],
                "pais": data["sys"]["country"],
                "temperatura": data["main"]["temp"],
                "sensacion_termica": data["main"]["feels_like"],
                "humedad": data["main"]["humidity"],
                "descripcion": data["weather"][0]["description"],
                "viento": data["wind"]["speed"]
            }
            return json.dumps(resultado, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Ciudad no encontrada o error en la API (código: {response.status_code})"})
    
    except Exception as e:
        return json.dumps({"error": f"Error al obtener el clima: {str(e)}"})


def calcular_descuento(precio: float, porcentaje: float) -> str:
    """
    Calcula el precio final de un producto aplicando un porcentaje de descuento.

    Args:
        precio: Precio original del producto.
        porcentaje: Porcentaje de descuento a aplicar (ej: 15 para 15%).

    Returns:
        str: Precio final con descuento en formato JSON.
    """
    resultado = float(precio) * (1 - float(porcentaje) / 100)
    return json.dumps({"precio_final": round(resultado, 2)})


# ============================================================
# PASO 2: Definir la nueva función que usa Serper
#
# Serper es un wrapper de Google Search con una API REST simple.
# Endpoint: POST https://google.serper.dev/search
# Headers requeridos:
#   - X-API-KEY: tu clave de Serper
#   - Content-Type: application/json
# Body: { "q": "<consulta>", "num": <cantidad de resultados>, "hl": "<idioma>" }
#
# La función devuelve SIEMPRE un string (json.dumps), porque eso
# es lo que el modelo espera recibir como resultado de una tool.
# ============================================================
def buscar_en_web(consulta: str, num_resultados: int = 5) -> str:
    """
    Realiza una búsqueda en Google usando la API de Serper y devuelve
    los resultados más relevantes.

    Args:
        consulta: Término o pregunta a buscar en Google.
        num_resultados: Cantidad de resultados a devolver (por defecto 5).

    Returns:
        str: Lista de resultados con título, enlace y fragmento, en formato JSON.
    """
    if not SERPER_API_KEY:
        return json.dumps({"error": "SERPER_API_KEY no configurada en el archivo .env"})

    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": consulta,
            "num": num_resultados,
            "hl": "es"         # Idioma de los resultados (es = español)
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Extraemos solo los campos útiles de los resultados orgánicos
            resultados = []
            for item in data.get("organic", []):
                resultados.append({
                    "titulo": item.get("title", ""),
                    "enlace": item.get("link", ""),
                    "fragmento": item.get("snippet", "")
                })

            return json.dumps({"consulta": consulta, "resultados": resultados}, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Error en Serper API (código: {response.status_code}): {response.text}"})

    except Exception as e:
        return json.dumps({"error": f"Error al realizar la búsqueda: {str(e)}"})


# ─────────────────────────────────────────────
# EL CONTRATO (JSON Schema) — qué puede hacer el agente
# ─────────────────────────────────────────────

# ============================================================
# PASO 3: Agregar la nueva herramienta a la lista `tools`
#
# Cada herramienta es un diccionario con:
#   - type: siempre "function"
#   - function.name: debe coincidir EXACTAMENTE con el nombre
#     de la función Python definida arriba.
#   - function.description: el modelo la usa para DECIDIR cuándo
#     invocar esta herramienta. Sé descriptivo y explícito.
#   - function.parameters: JSON Schema que define qué argumentos
#     acepta la función. El modelo los infiere del mensaje del usuario.
#
# Agregar una herramienta = agregar un dict a esta lista + 
# registrar la función en `available_functions` (PASO 4).
# ============================================================
tools = [
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
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_descuento",
            "description": "Calcula el precio final aplicando un porcentaje de descuento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "precio": {"type": "number"},
                    "porcentaje": {"type": "number"}
                },
                "required": ["precio", "porcentaje"]
            }
        }
    },
    # ── NUEVA HERRAMIENTA ──────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "buscar_en_web",
            "description": (
                "Realiza una búsqueda en Google y devuelve resultados actuales de internet. "
                "Úsala cuando el usuario pregunte por noticias, eventos recientes, información "
                "actualizada o cualquier tema que requiera datos en tiempo real que el modelo "
                "no puede conocer por su entrenamiento."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "La consulta o pregunta a buscar en Google (ej: 'últimas noticias sobre IA', 'precio del dólar hoy')"
                    },
                    "num_resultados": {
                        "type": "integer",
                        "description": "Cantidad de resultados a devolver. Por defecto 5, máximo 10.",
                        "default": 5
                    }
                },
                "required": ["consulta"]
            }
        }
    }
    # ──────────────────────────────────────────────────────────
]


# ============================================================
# PASO 4: Registrar la nueva función en el diccionario de despacho
#
# Este diccionario actúa como un "router": cuando el modelo
# devuelve un tool_call con name="buscar_en_web", el loop del
# agente busca aquí la función Python correspondiente y la ejecuta.
#
# Si olvidás agregar la función acá, el agente va a recibir
# el error "Función '...' no encontrada." en tiempo de ejecución.
# ============================================================
available_functions = {
    "obtener_clima": obtener_clima,
    "calcular_descuento": calcular_descuento,
    "buscar_en_web": buscar_en_web,   # ← nueva función registrada
}


def main():
    importlib.reload(config)
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    print("🤖 Agente Pro con Web Search iniciado. Escribí 'salir' para terminar.\n")
    print("💡 Ahora podés preguntar cosas como: '¿Cuáles son las últimas noticias sobre IA?'\n")

    while True:
        user_input = input("👤 Usuario: ").strip()
        if user_input.lower() == "salir":
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # LLAMADA 1: El modelo decide si responde directamente o usa una herramienta
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"   # "auto" = el modelo elige si usar tool o no
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Guardamos el mensaje del asistente con las tool_calls
            # (obligatorio en el historial antes de los resultados de tools)
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"🛠️  Ejecutando: {function_name} con args: {function_args}")
                function_to_call = available_functions.get(function_name)

                if function_to_call:
                    function_response = function_to_call(**function_args)
                else:
                    function_response = json.dumps({"error": f"Función '{function_name}' no encontrada."})

                print(f"📡 Resultado: {function_response}\n")

                # Resultado de la tool: role="tool" + tool_call_id vincula
                # este resultado con la solicitud específica del modelo
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response if isinstance(function_response, str) else json.dumps(function_response),
                })

            # LLAMADA 2: Con los resultados reales, el modelo genera la respuesta final
            final_response = client.chat.completions.create(
                model=config.MODEL,
                messages=messages
            )
            assistant_reply = final_response.choices[0].message.content
        else:
            # El modelo respondió directamente sin usar herramientas
            assistant_reply = response_message.content

        print(f"🤖 Asistente: {assistant_reply}\n")
        messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    main()
