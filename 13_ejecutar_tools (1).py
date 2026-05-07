import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))

# --- 🛠️ PASO 1: DEFINIR LAS HERRAMIENTAS REALES ---
def obtener_clima(ciudad):
    # En producción esto sería una llamada a una API real (OpenWeather)
    datos_clima = {
        "buenos aires": "24°C, Soleado",
        "cordoba": "28°C, Tormentas",
        "rosario": "22°C, Nublado",
        "mendoza": "10°C, Tormentas"
    }
    return datos_clima.get(ciudad.lower(), "Clima desconocido para esa ubicación.")

def calcular_descuento(precio, porcentaje):
    try:
        resultado = float(precio) * (1 - float(porcentaje)/100)
        return f"El precio final con descuento es ${resultado:.2f}"
    except:
        return "Error en los parámetros de cálculo."
    
    

# Diccionario de funciones disponibles para el agente
TOOLS = {
    "obtener_clima": obtener_clima,
    "calcular_descuento": calcular_descuento
}

# --- 🧠 PASO 2: SYSTEM PROMPT CON HERRAMIENTAS ---
SYSTEM_PROMPT = """
Sos un Agente que resuelve tareas paso a paso usando herramientas.

Herramientas disponibles:
- obtener_clima(ciudad)
- calcular_descuento(precio, porcentaje)

Seguí SIEMPRE este ciclo. En cada turno solo podés hacer UNA de estas dos cosas:

OPCIÓN A - Usar una herramienta (cuando necesitás información):
Thought: [tu razonamiento]
Action: nombre_herramienta(args)

OPCIÓN B - Dar la respuesta final (solo cuando ya tenés toda la información necesaria):
Thought: [tu razonamiento basado en las Observations recibidas]
Final Answer: [respuesta completa al usuario]

REGLAS IMPORTANTES:
- Nunca pongas Action y Final Answer en el mismo mensaje.
- Nunca inventes el resultado de una herramienta. Esperá la Observation.
- Cuando ves "Observation: ..." en el historial, ya tenés el resultado real. No vuelvas a llamar a esa herramienta.
- Solo usá Final Answer cuando ya tenés todos los datos para responder la consulta del usuario.
- No inventes herramientas ni acciones. Solo usá las que están listadas arriba.
- limtate a responder lo que se te pide. No agregues información extra ni explicaciones innecesarias.
"""

# funcion para extraer la accion pedida por el agente
def extraer_accion(texto):
    patron = r"Action:\s*(\w+)\((.*)\)"
    match = re.search(patron, texto)
    if match:
        func_name = match.group(1)
        args_str = match.group(2).replace("'", "").replace('"', "")
        args = []
        for a in args_str.split(","):
            a = a.strip()
            if "=" in a:
                a = a.split("=", 1)[1].strip()
            args.append(a.lower()) # Convertir a minúsculas para consistencia
        return func_name, args
    return None, None


# funcion principal
def main():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("🤖 Agente Ejecutor Real iniciado.")

    while True:
        user_input = input("\n👤 Usuario: ")
        if user_input.lower() == "salir": break
        history.append({"role": "user", "content": user_input})

        max_iter = 5 # maximo de iteraciones para ejecutar herramientas
        for _ in range(max_iter):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=history,
                temperature=0
            )
            output = response.choices[0].message.content
            print(f"\n🧠 Pensamiento: {output}")

            # Extraer la accion pedida
            func_name, args = extraer_accion(output)

            # Si el agente pidió ejecutar una herramienta, la ejecutamos y le damos el resultado real
            if func_name and func_name in TOOLS:
                print("\n")
                print(f"🛠️  Ejecutando: {func_name}({args})")
                
                # --- 🚀 PASO 3: EJECUCIÓN AUTOMÁTICA ---
                resultado_real = TOOLS[func_name](*args) 
                
                print(f"📡 Resultado: {resultado_real}")
                
                # Inyectamos la observación real al historial
                history.append({"role": "assistant", "content": output})
                history.append({"role": "user", "content": f"Observation: {resultado_real}"})
                continue # El bucle sigue para procesar el resultado
            
            elif "Final Answer:" in output:
                print(f"\n")
                print(f"✅ Respuesta: {output.split('Final Answer:')[1]}")
                break
            else:
                # El LLM no dio Action ni Final Answer: forzar una respuesta final
                history.append({"role": "assistant", "content": output})
                history.append({"role": "user", "content": "Por favor, proporcioná la respuesta final en el formato: Final Answer: [respuesta]"})
                continue

if __name__ == "__main__":
    main()