"""
agent_runner2.py — Variante del runner para el pipeline Generador-Evaluador.

Diferencia clave respecto a agent_runner.py:
  - run_agent()  →  imprime la respuesta y la agrega al historial (uso interactivo).
  - run_agent_silent()  →  ejecuta el agente y RETORNA la respuesta como string,
    sin imprimirla ni modificar el historial externo. Esto permite que el pipeline
    capture la respuesta y se la pase al evaluador antes de mostrarla al usuario.
"""

import json
import inspect
from openai import OpenAI, BadRequestError
from tools import TOOLS_SCHEMAS, AVAILABLE_FUNCTIONS


def run_agent_silent(client: OpenAI, model: str, system_prompt: str, user_input: str) -> str:
    """
    Ejecuta un turno completo del agente de forma silenciosa y retorna la respuesta.

    A diferencia de run_agent(), este runner:
      - Construye su propio historial interno (no modifica el del caller).
      - No imprime nada (el pipeline decide qué mostrar y cuándo).
      - Retorna la respuesta final como string para que el evaluador la audite.

    Args:
        client:        Instancia del cliente OpenAI/Groq.
        model:         Nombre del modelo generador.
        system_prompt: El system prompt del generador.
        user_input:    La consulta del usuario (puede incluir feedback del evaluador).

    Returns:
        str: La respuesta final del agente.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_input},
    ]

    # ── LLAMADA 1: ¿el modelo quiere usar una herramienta? ──
    # BadRequestError aquí indica que el modelo generó un nombre de tool
    # malformado (ej: 'busy=buscar_en_web'). Groq rechaza la petición antes
    # de ejecutar nada. Recuperamos reintentando sin tools: el modelo responde
    # directamente con lo que sabe, y el pipeline puede seguir su ciclo normal.
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS_SCHEMAS,
            tool_choice="auto"
        )
    except BadRequestError as e:
        print(f"   ⚠️  Tool call malformado — reintentando sin herramientas. ({e.status_code})")
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        # El modelo a veces incluye "razonamiento previo" en el content
        # de la llamada 1 (ej: "Voy a usar buscar_en_web para...").
        # Si lo dejamos en el historial, puede colarse en la respuesta final.
        # Lo borramos: el historial solo necesita los tool_calls, no ese texto.
        response_message.content = None
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"   🛠️  Herramienta usada: {function_name} con args: {function_args}")

            fn = AVAILABLE_FUNCTIONS.get(function_name)
            if fn:
                # Filtramos kwargs que el LLM inventó y no existen en la firma
                # real de la función (ej: 'timestamp', 'format', etc.).
                valid_params = inspect.signature(fn).parameters
                function_args = {k: v for k, v in function_args.items() if k in valid_params}
                result = fn(**function_args)
            else:
                result = json.dumps({"error": f"Función '{function_name}' no encontrada."})

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "name":         function_name,
                "content":      result if isinstance(result, str) else json.dumps(result),
            })

        # ── LLAMADA 2: respuesta final con los resultados de las tools ──
        try:
            final_response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return final_response.choices[0].message.content
        except BadRequestError as e:
            print(f"   ⚠️  Error en llamada final ({e.status_code}) — devolviendo respuesta parcial.")
            return response_message.content or ""

    return response_message.content
