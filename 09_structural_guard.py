import os
import json
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

# THE STRUCTURAL GUARD
# =====================
# Desafío: Cuando el usuario pide datos de una persona (nombre, edad, email),
# el modelo debe responder SOLO en formato JSON válido.
# Si el JSON es inválido, detectamos el error y pedimos corrección automáticamente.

history = [
    {
        "role": "system",
        "content": (
            "Sos un asistente útil. "
            "Cuando el usuario pida 'datos de usuario', 'información personal' o similar, "
            "respondé EXCLUSIVAMENTE con un JSON válido con este formato exacto:\n"
            '{"nombre": "...", "edad": ..., "email": "..."}\n'
            "Sin texto adicional, sin explicaciones, solo el JSON. "
            "Para cualquier otra pregunta, respondé normalmente."
        )
    }
]

print("🤖 Structural Guard iniciado. Escribí 'salir' para terminar.\n")


def es_solicitud_de_datos(texto):
    """Detecta si el usuario está pidiendo datos de usuario."""
    palabras_clave = ["datos", "usuario", "información personal", "ficha", "contacto"]
    texto_lower = texto.lower()
    return any(palabra in texto_lower for palabra in palabras_clave)


def validar_json(respuesta_texto):
    """
    Intenta parsear el texto como JSON.
    Retorna (True, data) si es válido, (False, error) si no lo es.
    """
    try:
        # Intentamos convertir el string a diccionario Python
        data = json.loads(respuesta_texto)

        # Verificamos que tenga las claves requeridas
        campos_requeridos = ["nombre", "edad", "email"]
        faltantes = [campo for campo in campos_requeridos if campo not in data]

        if faltantes:
            return False, f"Faltan campos: {faltantes}"

        return True, data

    except json.JSONDecodeError as e:
        return False, f"JSON inválido: {e}"


def pedir_correccion(respuesta_mala, error_detectado):
    """
    Cuando el JSON es inválido, enviamos un mensaje al modelo
    pidiendo que corrija la respuesta.
    """
    mensaje_correccion = {
        "role": "user",
        "content": (
            f"Tu respuesta anterior no es un JSON válido. Error: {error_detectado}\n"
            f"Respuesta anterior: {respuesta_mala}\n"
            "Por favor, corregí y devolvé SOLO el JSON válido con el formato: "
            '{"nombre": "...", "edad": ..., "email": "..."}'
        )
    }
    return mensaje_correccion


while True:
    user_input = input("👤 Vos: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        print("👋 ¡Hasta luego!")
        break

    # Agregamos el mensaje del usuario
    history.append({"role": "user", "content": user_input})

    # Detectamos si es una solicitud de datos estructurados
    requiere_json = es_solicitud_de_datos(user_input)

    if requiere_json:
        print("📋 Detecté solicitud de datos. Esperando JSON...")

    # Hacemos la llamada a la API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        temperature=0.1,  # Baja temperatura para respuestas más deterministas
        max_tokens=200
    )

    respuesta_texto = response.choices[0].message.content

    # SI es una solicitud de datos, validamos el JSON
    if requiere_json:
        es_valido, resultado = validar_json(respuesta_texto)

        if es_valido:
            # Éxito: JSON válido con todos los campos
            print(f"✅ JSON válido recibido:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))

            # Guardamos en el historial como mensaje del assistant
            history.append({
                "role": "assistant",
                "content": respuesta_texto
            })

        else:
            # ERROR: El modelo no devolvió JSON válido
            print(f"❌ JSON inválido detectado: {resultado}")
            print(f"📝 Respuesta cruda: {respuesta_texto[:100]}...")
            print("🔄 Solicitando corrección automática...\n")

            # Pedimos corrección al modelo
            correccion = pedir_correccion(respuesta_texto, resultado)
            history.append(correccion)

            # Llamamos de nuevo para obtener la corrección
            response2 = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=history,
                temperature=0.1,
                max_tokens=200
            )

            respuesta_corregida = response2.choices[0].message.content
            es_valido2, resultado2 = validar_json(respuesta_corregida)

            if es_valido2:
                print(f"✅ Corrección exitosa:")
                print(json.dumps(resultado2, indent=2, ensure_ascii=False))
                history.append({
                    "role": "assistant",
                    "content": respuesta_corregida
                })
            else:
                print(f"❌ La corrección también falló: {resultado2}")
                print(f"Respuesta: {respuesta_corregida}")

                # Como último recurso, guardamos la respuesta original
                history.append({
                    "role": "assistant",
                    "content": respuesta_texto
                })

    else:
        # Respuesta normal (no requiere JSON)
        print(f"🤖 IA: {respuesta_texto}\n")
        history.append({
            "role": "assistant",
            "content": respuesta_texto
        })

print("\n=== DESAFÍO COMPLETADO ===")
print("Conceptos aplicados:")
print("- Detección de intención (¿el usuario quiere datos estructurados?)")
print("- Validación de JSON con json.loads()")
print("- Reintentos automáticos cuando la estructura es inválida")
print("- Separación entre respuestas libres y respuestas estructuradas")
