import os
import json
import importlib
import requests
from dotenv import load_dotenv
from openai import OpenAI
import config
from Tools import TOOLS_SCHEMA, AVAILABLE_FUNCTIONS

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
print(f"WEATHER_API_KEY: {WEATHER_API_KEY}")
print(f"GROQ_API_KEY: {GROQ_API_KEY}")
print(f"SERPER_API_KEY: {SERPER_API_KEY}")

if not GROQ_API_KEY:
    #raise ValueError("GROQ_API_KEY no configurada en el archivo .env")
    GROQ_API_KEY = ""
if not WEATHER_API_KEY:
    #raise ValueError("WEATHER_API_KEY no configurada en el archivo .env")
    WEATHER_API_KEY = ""
#print(f"WEATHER_API_KEY: {WEATHER_API_KEY}")
#print(f"GROQ_API_KEY: {GROQ_API_KEY}")
print(f"MODEL: {config.MODEL}")

#client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
#WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY1")
#OPENAI_API_KEY="sk-proj---8PzYhc5-_6SEoIx_eFfDAA"

print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no configurada en el archivo .env")

client = OpenAI(api_key=OPENAI_API_KEY)


# Las tools y sus funciones se importan desde Tools.py

def main():
    # Cargamos la configuración desde config.py (reload permite cambiarlo en caliente)
    importlib.reload(config)
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    print("🤖 Agente Pro iniciado. Escribí 'salir' para terminar.\n")

    while True:
        user_input = input("👤 Dale, decime que queres : ").strip()
        if user_input.lower() == "salir":
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # LLAMADA 1: El modelo decide si responde o usa una herramienta
        # el GROQ me RESTRINGE
        #response = client.chat.completions.create(
        #    model=config.MODEL,
        #    messages=messages,
        #    tools=tools,
        #    tool_choice="auto"
        #)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0.7
        )

        #print(f"RESPONSE  : {response}\n")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Guardamos el mensaje del asistente con las tool_calls (obligatorio antes de los tool results)
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"🛠️  Ejecutando {function_name} con {function_args}")
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

                if function_to_call:
                    function_response = function_to_call(**function_args)
                else:
                    function_response = json.dumps({"error": f"Función '{function_name}' no encontrada."})

                print(f"📡 Resultado: {function_response}\n")

                # Respuesta de la tool: role "tool" + tool_call_id vincula el resultado con la solicitud
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response if isinstance(function_response, str) else json.dumps(function_response),
                })

            # LLAMADA 2: Con los resultados reales, el modelo genera la respuesta final
            #final_response = client.chat.completions.create(
            #    model=config.MODEL,
            #    messages=messages
            #)
            final_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )
            assistant_reply = final_response.choices[0].message.content
        else:
            # El modelo respondió directo sin usar herramientas
            assistant_reply = response_message.content

        print(f"🤖 Asistente: {assistant_reply}\n")
        # Guardamos la respuesta del asistente en el historial
        messages.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    main()
