import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# api_key = os.environ.get("GROQ_API_KEY")
# if not api_key:
#     print("Error: No se encontró GROQ_API_KEY")
#     exit(1)

# client = OpenAI(
#     base_url="https://api.groq.com/openai/v1",
#     api_key=api_key
# )

# OPENAI_API_KEY hardcoded
api_key = "sk-proj---8PzYhc5-_6SEoIx_eFfDAA"
client = OpenAI(api_key=api_key)

# EL CHAT LOOP: El corazón de un agente conversacional
# ===================================================
# Un agente no es una sola llamada a la API. Es un BUCLE (loop) que:
# 1. Escucha al usuario
# 2. Envía el mensaje a la API (con todo el historial)
# 3. Muestra la respuesta
# 4. GUARDA la respuesta para la siguiente vuelta (memoria)

# Historial de la conversación. Empieza con el "system" (la personalidad)
history = [
    {"role": "system", "content": "Sos un asistente técnico experto en Python. Respondé de forma clara y concisa."}
]

print("🤖 Agente iniciado. Escribí 'salir' para terminar.\n")

while True:
    # PASO 1: Capturar entrada del usuario
    user_input = input("👤 Vos: ")
    
    # Salir si escribe "salir", "exit" o "quit"
    if user_input.lower() in ["salir", "exit", "quit"]:
        print("👋 ¡Hasta luego!")
        break
    
    # PASO 2: Agregar mensaje del usuario al historial
    # Esto es CRÍTICO: la API no recuerda nada, nosotros le pasamos TODO
    history.append({"role": "user", "content": user_input})
    
    # PASO 3: Llamar a la API enviando TODO el historial
    # Cuanto más larga la conversación, más mensajes enviamos
    #model="llama-3.1-8b-instant",
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=history,
        temperature=0.7,
        max_tokens=150
    )
    
    # PASO 4: Extraer la respuesta del modelo
    # response.choices[0].message es un objeto con role="assistant" y content="..."
    assistant_message = response.choices[0].message
    
    # PASO 5: MOSTRAR la respuesta al usuario
    print(f"🤖 IA: {assistant_message.content}\n")
    
    # PASO 6: GUARDAR la respuesta en el historial
    # Esto permite que en la siguiente vuelta, la IA "recuerde" lo que dijo
    # Sin este paso, la IA no sabría que ya respondió algo
    history.append({
        "role": "assistant",
        "content": assistant_message.content
    })
    
    # OPCIONAL: Ver cuántos mensajes tenemos en memoria
    # print(f"[Debug: {len(history)} mensajes en historial]")

# Después de salir del while, podemos ver todo el historial
print("\n=== HISTORIAL COMPLETO DE LA CONVERSACIÓN ===")
for i, msg in enumerate(history):
    # No mostrar el system (es largo y técnico)
    if msg["role"] == "system":
        continue
    emoji = "👤" if msg["role"] == "user" else "🤖"
    print(f"{i}: {emoji} {msg['role']}: {msg['content'][:60]}...")

# CONCEPTOS CLAVE:
# - La lista 'history' es la MEMORIA del agente
# - Cada vuelta del while es un "turno" de conversación
# - Sin guardar el mensaje del assistant, el agente pierde el hilo
# - En producción, habría que limitar el tamaño del historial (ej: últimos 20 mensajes)
