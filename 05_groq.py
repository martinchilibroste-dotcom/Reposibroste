import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("Error: No se encontró GROQ_API_KEY")
    print("Crea un archivo .env con: GROQ_API_KEY=tu-api-key")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

respuesta = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Decime un dato curioso sobre gatos"}],
    max_tokens=100
)

print("=== OBJETO COMPLETO DE RESPUESTA ===")
print(respuesta)
print()

print("=== ATRIBUTOS DISPONIBLES ===")
print(dir(respuesta))
