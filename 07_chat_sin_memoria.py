import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Error: No se encontró GROQ_API_KEY")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# CHAT SIN MEMORIA
# =================
# Cada mensaje es una llamada INDEPENDIENTE a la API.
# La IA NO recuerda lo que dijiste en el mensaje anterior.
# Solo le enviamos el system + tu mensaje actual.

print("🤖 Agente iniciado (SIN memoria). Escribí 'salir' para terminar.\n")

while True:
    # Capturar entrada del usuario
    user_input = input("👤 Vos: ")
    
    if user_input.lower() in ["salir", "exit", "quit"]:
        print("👋 ¡Hasta luego!")
        break
    
    # CADA llamada es INDEPENDIENTE
    # Solo enviamos: system + el mensaje actual del usuario
    # No hay historial de mensajes anteriores
    messages = [
        {"role": "system", "content": "Sos un asistente técnico experto en Python."},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,  # Siempre son solo 2 mensajes
        temperature=0.7,
        max_tokens=150
    )
    
    answer = response.choices[0].message.content
    print(f"🤖 IA: {answer}\n")
    
    # NOTA: NO guardamos la respuesta en ningún lado
    # La próxima vuelta del while arranca desde cero

print("\n=== CONVERSACIÓN TERMINADA ===")
print("Cada mensaje fue una llamada nueva. La IA no 'recordaba' nada.")
