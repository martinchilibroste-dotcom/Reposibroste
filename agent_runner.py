"""
agent_runner.py — Loop de ejecución del agente.

Este módulo se ocupa ÚNICAMENTE de orquestar la conversación:
  1. Recibir el input del usuario.
  2. Enviar los mensajes al LLM.
  3. Detectar si el LLM quiere usar una herramienta.
  4. Ejecutarla y devolverle el resultado al LLM.
  5. Imprimir la respuesta final.

No sabe nada de qué herramientas existen ni cómo funcionan:
esa responsabilidad es 100% de tools.py.
"""

import json
from xmlrpc import client
from openai import OpenAI
from Tools import TOOLS_SCHEMA, AVAILABLE_FUNCTIONS


def run_agent(client: OpenAI, model: str, messages: list) -> None:
    """
    Ejecuta un turno completo del agente: recibe los mensajes actuales,
    llama al LLM, ejecuta herramientas si es necesario y agrega la
    respuesta final al historial.

    Args:
        client:   Instancia del cliente OpenAI/Groq.
        model:    Nombre del modelo a usar (ej: "llama-3.3-70b-versatile").
        messages: Lista de mensajes del historial (se modifica en lugar).
    """
    # ── LLAMADA 1: el LLM decide si responder o usar una herramienta ──
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )
    

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        # El mensaje del asistente con los tool_calls debe ir al historial
        # ANTES de agregar los resultados; es un requisito del protocolo.
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"🛠️  Ejecutando: {function_name} con args: {function_args}")

            fn = AVAILABLE_FUNCTIONS.get(function_name)
            if fn:
                result = fn(**function_args)
            else:
                result = json.dumps({"error": f"Función '{function_name}' no encontrada."})

            print(f"📡 Resultado: {result}\n")

            # role="tool" + tool_call_id vincula el resultado con la solicitud
            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "name":         function_name,
                "content":      result if isinstance(result, str) else json.dumps(result),
            })

        # ── LLAMADA 2: el LLM genera la respuesta final con los resultados ──
        final_response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        assistant_reply = final_response.choices[0].message.content

    else:
        # El LLM respondió directamente sin invocar ninguna herramienta
        assistant_reply = response_message.content

    print(f"🤖 Asistente: {assistant_reply}\n")
    messages.append({"role": "assistant", "content": assistant_reply})
