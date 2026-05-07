"""
12_react_parsing.py
===================
AGENTE ReAct CON PARSING AUTOMÁTICO (Evolución del Ejemplo 11)

DIFERENCIA CLAVE RESPECTO AL EJEMPLO 11:
----------------------------------------
- Ejemplo 11: El humano lee y decide qué herramienta pidió el agente
- Ejemplo 12: El código parsea AUTOMÁTICAMENTE la Action con Regex
- Además, usa un BUCLE INTERNO que permite múltiples pasos de razonamiento

¿QUÉ ES EL PARSING AUTOMÁTICO?
------------------------------
La función extraer_accion() usa una expresión regular para detectar:
    Action: buscar_clima(Buenos Aires)
           ↑ herramienta    ↑ argumento

Esto permite que el sistema "entienda" qué quiere hacer el agente sin
intervención humana. Es el puente hacia agentes 100% automatizados.

FLUJO DEL BUCLE INTERNO:
------------------------
Usuario pregunta
    ↓
Agente genera Thought + Action
    ↓
Regex detecta Action → muestra herramienta + argumento al usuario
    ↓
Usuario ingresa Observation (simulando el resultado real)
    ↓
Observation se agrega al historial
    ↓
(LOOP) Agente procesa con nueva información
    ↓
Final Answer detectado → responde y sale del bucle interno

CÓMO USAR EN CLASE:
-------------------
1. Preparación:
   - Crear archivo .env con: GROQ_API_KEY=tu_api_key_aquí
   - Activar entorno virtual: .\venv\Scripts\activate
   - Ejecutar: python 12_react_parsing.py

2. Durante la ejecución:
   - El alumno escribe una consulta que requiera múltiples pasos
   - El sistema detecta automáticamente la herramienta solicitada
   - El alumno ingresa la Observation
   - Si el agente necesita más datos, el bucle continúa automáticamente
   - Finalmente el agente genera la respuesta completa

3. Ejemplo de sesión:
   👤 Usuario: ¿Cuál es la distancia entre Buenos Aires y Córdoba?
   
   --- 🧠 PENSAMIENTO DEL AGENTE ---
   Thought: El usuario quiere saber la distancia entre dos ciudades.
            Necesito usar calcular_distancia.
   Action: calcular_distancia(Buenos Aires, Córdoba)
   
   🛠️  [SISTEMA]: El Agente solicitó la herramienta: calcular_distancia
   📦 [SISTEMA]: Argumentos detectados: Buenos Aires, Córdoba
   📝 Ingresá el resultado: 700 km
   
   ✅ RESPUESTA FINAL: La distancia entre Buenos Aires y Córdoba es de 700 km.

PARA SALIR:
-----------
Escribir: salir

REQUISITOS:
-----------
- Archivo .env con GROQ_API_KEY
- Dependencias: pip install openai python-dotenv

CONCEPTO CLAVE:
---------------
Este ejemplo demuestra cómo el código puede "interpretar" las intenciones
del modelo y ejecutar lógica basada en eso. Es la base de frameworks como
LangChain o CrewAI, donde el agente decide qué herramientas usar dinámicamente.
"""

import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# 1. Configuración inicial
load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1", 
    api_key=os.getenv("GROQ_API_KEY")
)

# 2. El System Prompt: Define las reglas del patrón ReAct
SYSTEM_PROMPT = """
Sos un Agente de Investigación Autónomo. No respondas directamente al usuario.
Debés seguir este proceso estrictamente para cada paso:

1. Thought: Razoná sobre qué información te falta y qué herramienta necesitás.
2. Action: Si necesitás datos externos, escribí EXACTAMENTE: Action: nombre_herramienta(argumento)
3. Observation: Esperá a que el sistema te devuelva el resultado de esa acción.

Formato de respuesta:
Thought: [Tu razonamiento]
Action: [herramienta(parámetro)]
Final Answer: [Tu respuesta final solo cuando tengas la solución]

Herramientas disponibles:
- buscar_clima(ciudad): Devuelve el clima actual.
- calcular_distancia(origen, destino): Devuelve la distancia en km.

Da la respuesta final solo cuando tengas la solución.
Respuesta final: [Tu respuesta final]
"""

def extraer_accion(texto):
    """
    Función del Ejemplo 12: Usa Regex para capturar la intención del Agente.
    """
    patron = r"Action:\s*(\w+)\((.*)\)"
    match = re.search(patron, texto)
    if match:
        return match.group(1), match.group(2)
    return None, None

def main():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("🤖 Agente ReAct con Parsing Automático iniciado.")
    print("Escribí 'salir' para terminar.\n")

    while True:
        user_input = input("👤 Usuario: ")
        if user_input.lower() == "salir":
            break

        history.append({"role": "user", "content": user_input})

        # BUCLE DE RAZONAMIENTO
        while True:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=history,
                temperature=0  # Cero para máxima precisión técnica
            )
            
            agente_output = response.choices[0].message.content
            print(f"\n--- 🧠 PENSAMIENTO DEL AGENTE ---\n{agente_output}")

            # PASO CLAVE: Usamos el código del Ejemplo 12 para parsear la respuesta
            func, arg = extraer_accion(agente_output)

            if func:
                print(f"\n🛠️  [SISTEMA]: El Agente solicitó la herramienta: {func}")
                print(f"📦 [SISTEMA]: Argumentos detectados: {arg}")
                
                # En la Clase 2, la observación sigue siendo simulada por nosotros
                obs = input(f"📝 Ingresá el resultado (Observation) para {func}: ")
                
                # Guardamos el pensamiento y la observación en el historial
                history.append({"role": "assistant", "content": agente_output})
                history.append({"role": "user", "content": f"Observation: {obs}"})
                
                # El bucle interno continúa para que el modelo procese la Observation
                continue 
            
            elif "Respuesta final:" in agente_output:
                print(f"\n✅ RESPUESTA FINAL: {agente_output.split('Respuesta final:')[1].strip()}")
                history.append({"role": "assistant", "content": agente_output})
                break
            else:
                # Fallback por si el modelo no sigue el formato
                print(f"\n🤖 IA: {agente_output}")
                break

if __name__ == "__main__":
    main()