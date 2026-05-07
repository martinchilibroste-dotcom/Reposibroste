# Script sencillo para probar la API de OpenAI
# Requiere: crear archivo .env con OPENAI_API_KEY=tu-api-key

import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables desde archivo .env
load_dotenv()

# Obtener API key de variable de entorno
#api_key = os.environ.get("OPENAI_API_KEY")

# OPENAI_API_KEY hardcoded
api_key = "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"

if not api_key:
    print("Error: No se encontró OPENAI_API_KEY")
    print("Crea un archivo .env con: OPENAI_API_KEY=tu-api-key")
    exit(1)

#print(f"API Key: {api_key}")
#exit(1)

men1 = "Decime un dato curioso sobre gatos"

while True:
    consul = input("Meta su consulta:")
    if consul == "salir":
        print("chauuuuuuu...")
        break       #exit(0)
    if len(consul) > 1:
        print("Consulta ingresada:", consul)
        mensa = {"role": "user", "content": consul}
        print(mensa)
    else:
        mensa = {"role": "user", "content": men1}
        print(mensa)

    client = OpenAI(api_key=api_key)

    # Hacer la llamada a la API
    respuesta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[mensa],
        max_tokens=100
    )

    # Imprimir el objeto completo (no solo el texto)
    #print("=== OBJETO COMPLETO DE RESPUESTA ===")
    #print(respuesta)
    #print()

    print("=== Mensaje DE la RESPUESTA ===")
    print(respuesta.choices[0].message.content)
    print()

    # También podés ver atributos específicos
    #print("=== ATRIBUTOS DISPONIBLES ===")
    #print(dir(respuesta))
