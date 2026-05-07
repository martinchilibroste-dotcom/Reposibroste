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

# EL JUEGO DE LOS ROLES
# La API no "recuerda" nada por sí sola. Nosotros le pasamos el historial
# completo en cada llamada. Es una lista de mensajes con 3 roles posibles:

# - "system": Define la personalidad y reglas del asistente (se pone una sola vez al inicio)
# - "user": Lo que escribe la persona
# - "assistant": Lo que responde la IA

# Ejemplo: Chatbot para una veterinaria que SOLO habla de perros

contexto = [
    # SYSTEM: El "manual de instrucciones" del asistente
    {"role": "system", "content": "Sos un experto veterinario. Solo respondés sobre perros."},

    # USER: La primera pregunta de la persona
    {"role": "user", "content": "Mi gato no come."},

    # ASSISTANT: La respuesta que dio la IA (la guardamos para que "recuerde")
    {"role": "assistant", "content": "Lo siento, solo puedo ayudarte con perros."},

    # USER: Una nueva pregunta (ahora sí sobre perros)
    {"role": "user", "content": "Bueno, ¿qué raza de perro es más tranquila?"}
]

print("=== CONTEXTO COMPLETO (4 mensajes) ===")
for i, msg in enumerate(contexto):
    print(f"{i}: {msg['role']}: {msg['content'][:50]}...")
print()

# Hacemos la llamada con TODO el contexto
respuesta = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=contexto,
    max_tokens=100
)

respuesta_ia = respuesta.choices[0].message.content
print(f"🤖 IA (con contexto completo): {respuesta_ia}")
print()

# # EXPERIMENTO 1: ¿Qué pasa si borramos el SYSTEM?
# print("=== EXPERIMENTO 1: Sin el mensaje 'system' ===")
# contexto_sin_system = contexto[1:]  # Sacamos el primer elemento (system)

# for i, msg in enumerate(contexto_sin_system):
#     print(f"{i}: {msg['role']}: {msg['content'][:50]}...")
# print()

# respuesta2 = client.chat.completions.create(
#     model="llama-3.1-8b-instant",
#     messages=contexto_sin_system,
#     max_tokens=100
# )

# print(f"🤖 IA (sin system): {respuesta2.choices[0].message.content}")
# print()

# # EXPERIMENTO 2: ¿Qué pasa si borramos el ASSISTANT?
# print("=== EXPERIMENTO 2: Sin el mensaje 'assistant' ===")
# # Lista solo con system y las preguntas del user (sin la respuesta de la IA)
# contexto_sin_assistant = [
#     contexto[0],  # system
#     contexto[1],  # user: "Mi gato no come"
#     contexto[3]   # user: "Bueno, ¿qué raza..."
# ]

# for i, msg in enumerate(contexto_sin_assistant):
#     print(f"{i}: {msg['role']}: {msg['content'][:50]}...")
# print()

# respuesta3 = client.chat.completions.create(
#     model="llama-3.1-8b-instant",
#     messages=contexto_sin_assistant,
#     max_tokens=100
# )

# print(f"🤖 IA (sin assistant): {respuesta3.choices[0].message.content}")
# print()

# CONCLUSIÓN:
# - Sin SYSTEM: La IA no sabe que debe hablar solo de perros
# - Sin ASSISTANT: La IA no "recuerda" que ya te respondió antes
# - Cada llamada a la API es independiente, por eso le pasamos TODO el historial
