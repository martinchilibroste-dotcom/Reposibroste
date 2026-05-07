"""
11_react_manual.py
==================
SIMULACIÓN MANUAL DEL PATRÓN ReAct (Reasoning + Acting)

OBJETIVO PEDAGÓGICO:
Este script permite a los alumnos experimentar manualmente el ciclo ReAct
antes de automatizarlo con código. El alumno "hace de Python" proporcionando
las observaciones que el agente necesita para completar su razonamiento.

¿QUÉ ES ReAct?
--------------
ReAct = Reasoning (Razonamiento) + Acting (Acción)
Es un patrón donde el modelo:
1. PIENSA (Thought) → 2. ACTÚA (Action) → 3. OBSERVA (Observation) → Repite → Responde

CÓMO USAR EN CLASE:
-------------------
1. Preparación:
   - Crear archivo .env con: GROQ_API_KEY=tu_api_key_aquí
   - Activar entorno virtual: .\venv\Scripts\activate
   - Ejecutar: python 11_react_manual.py

2. Durante la ejecución:
   - El alumno escribe una consulta (ej: "¿Qué clima hace en Córdoba?")
   - El agente responde con Thought + Action
   - El alumno debe ingresar manualmente la Observation (simulando el resultado
     de la herramienta, ej: "28°C, soleado")
   - El agente procesa la observación y genera Final Answer

3. Ejemplo de sesión:
   👤 Usuario: ¿Qué clima hace en Buenos Aires?
   
   --- 🧠 RAZONAMIENTO DEL AGENTE ---
   Thought: El usuario consulta por el clima. Necesito usar buscar_clima.
   Action: buscar_clima(Buenos Aires)
   
   🛠️ [SIMULACIÓN] Ingresá el resultado: 22°C, parcialmente nublado
   
   🤖 IA: El clima en Buenos Aires es de 22°C con cielo parcialmente nublado.

PARA SALIR:
-----------
Escribir: salir

REQUISITOS:
-----------
- Archivo .env con GROQ_API_KEY
- Dependencias: pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# OPENAI_API_KEY hardcoded, para chatGPT-4.1-mini
api_key_gpt = "sk-proj---8PzYhc5-_6SEoIx_eFfDAA"
clientgpt = OpenAI(api_key=api_key_gpt)

load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", 
                #api_key=os.getenv("GROQ_API_KEY")
                api_key="")

# El System Prompt es el "Sistema Operativo" de nuestro agente
SYSTEM_PROMPT = """
Sos un Agente de Investigación. No respondas directamente. 
Debés seguir este proceso paso a paso:

1. Thought: Razoná sobre qué necesitás hacer.
2. Action: Decidí qué acción tomar (usar herramientas).
3. Observation: Analizá el resultado de la acción.

Formato de respuesta obligatorio:
Thought: [Tu razonamiento]
Action: [Nombre de la herramienta y parámetros]
Final Answer: [Tu respuesta final al usuario]

Herramientas disponibles:
- buscar_clima(ciudad): Devuelve la temperatura actual.
- calcular_distancia(origen, destino): Devuelve km entre ciudades.
"""

history = [{"role": "system", "content": SYSTEM_PROMPT}]

print("🤖 Agente ReAct (Simulado) iniciado.")

while True:
    user_input = input("\n👤 Usuario: ")
    if user_input.lower() == "salir": break
    
    history.append({"role": "user", "content": user_input})
    
    # El modelo genera el Thought y la Action
    #response = client.chat.completions.create(
    #    model="llama-3.1-8b-instant",
    #    messages=history,
    #    temperature=0 # Queremos precisión, no creatividad
    #)
    
    # Hacer la llamada a la API de chatGPT
    response = clientgpt.chat.completions.create(
        model="gpt-4.1-mini",
        messages=history,
        temperature=0 # Queremos precisión, no creatividad
    )

    #Tip PRO: Groq usa modelos como:
    #llama3-70b-8192
    #mixtral-8x7b
    #Son muy rápidos (su fuerte es inferencia)

    agente_output = response.choices[0].message.content
    
    print(f"\n--- 🧠 RAZONAMIENTO DEL AGENTE ---\n{agente_output}")
    
    # En esta fase manual, el alumno hace de "Python" y le da la observación
    if "Action:" in agente_output:
        obs = input("\n🛠️ [SIMULACIÓN] Ingresá el resultado de la herramienta (Observation): ")
        history.append({"role": "assistant", "content": agente_output})
        history.append({"role": "user", "content": f"Observation: {obs}"})
        
        # Segunda llamada para que el agente procese la observación
        #final_res = client.chat.completions.create(
        #    model="llama-3.1-8b-instant",
        #    messages=history
        #)
        # Hacer la llamada a la API de chatGPT
        final_res = clientgpt.chat.completions.create(
            model="gpt-4.1-mini",
            messages=history,
            temperature=0 # Queremos precisión, no creatividad
        )
        print(f"\n🤖 IA: {final_res.choices[0].message.content}")
