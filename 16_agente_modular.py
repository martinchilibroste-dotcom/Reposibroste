"""
16_agente_modular.py — Punto de entrada del agente modularizado.

Responsabilidad de cada módulo:
  ┌─────────────────────┬──────────────────────────────────────────────┐
  │ tools.py            │ Funciones reales + esquemas JSON + router    │
  │ agent_runner.py     │ Loop LLM → herramienta → respuesta           │
  │ 16_agente_modular.py│ Configuración, historial, input del usuario  │
  └─────────────────────┴──────────────────────────────────────────────┘

Ventaja: para agregar una herramienta nueva solo se toca tools.py.
El resto del código no cambia.
"""

import os
import importlib
from dotenv import load_dotenv
from openai import OpenAI

import config
from agent_runner import run_agent

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY1")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no configurada en el archivo .env")

#coneccion usando OpenAI directamente, un fierro
client = OpenAI(api_key=OPENAI_API_KEY)
modelo = config.MODEL_GPT

#Coneccion usando Groq (me restringe no se xq, no funciona bien)
#client = OpenAI(
#    base_url="https://api.groq.com/openai/v1",
#    api_key=os.getenv("GROQ_API_KEY")
#)

#Coneccion usando DeepSeek (funciona bien, pero no es gratis)
#DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
#modelo = config.MODEL_DEEPSEEK
#print(f"DEEPSEEK_API_KEY: {DEEPSEEK_API_KEY} y modelo: {modelo}")
#client = OpenAI(
#    api_key=DEEPSEEK_API_KEY,
#    base_url="https://api.deepseek.com/v1"
#)

# 👇 Coneccion OpenRouter que usa DeepSeek gratis limitado, pero tambien quieren ver guita
#client = OpenAI(
#    api_key="sk-or-v1-2ed18........c6ad4d27075de7e",  # <-- La clave que copiaste
#    base_url="https://openrouter.ai/api/v1",  # <-- Cambia a OpenRouter
#)

def main():
    importlib.reload(config)

    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    print("🤖 Agente Modular iniciado. Escribí 'salir' para terminar.\n")

    while True:
        user_input = input("👤 Usuario: ").strip()
        if user_input.lower() == "salir":
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Delegamos toda la lógica de llamadas al LLM a agent_runner
        run_agent(client, modelo, messages)


if __name__ == "__main__":
    main()
