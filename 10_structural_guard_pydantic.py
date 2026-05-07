import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Error: No se encontró GROQ_API_KEY")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


# PYDANTIC: Definimos la estructura EXACTA que queremos recibir
# =============================================================
# Esto reemplaza la validación manual con json.loads()
# Pydantic valida tipos automáticamente y da errores descriptivos

class DatosUsuario(BaseModel):
    """Esquema de datos que el modelo debe devolver."""
    nombre: str
    edad: int
    email: str


# Historial con instrucciones claras sobre el formato JSON requerido
history = [
    {
        "role": "system",
        "content": (
            "Sos un asistente útil. "
            "Cuando el usuario pida 'datos de usuario', 'información personal' o similar, "
            "respondé EXCLUSIVAMENTE con un JSON válido con estos campos exactos: "
            "nombre (string), edad (número entero), email (string).\n"
            "Ejemplo: {\"nombre\": \"Ana\", \"edad\": 28, \"email\": \"ana@test.com\"}\n"
            "Sin texto adicional, sin explicaciones, solo el JSON."
        )
    }
]

print("🤖 Structural Guard con Pydantic iniciado. Escribí 'salir' para terminar.\n")


def es_solicitud_de_datos(texto):
    """Detecta si el usuario está pidiendo datos de usuario."""
    palabras_clave = ["datos", "usuario", "información personal", "ficha", "contacto"]
    return any(palabra in texto.lower() for palabra in palabras_clave)


def validar_con_pydantic(respuesta_texto):
    """
    Usa Pydantic para validar que el JSON tenga la estructura correcta.
    Retorna (True, datos) o (False, error).
    """
    try:
        # Primero parseamos el string a dict
        data_dict = json.loads(respuesta_texto)

        # Luego validamos con Pydantic (chequea tipos y campos)
        datos_validados = DatosUsuario.model_validate(data_dict)

        # Convertimos a dict para mostrar
        return True, datos_validados.model_dump()

    except json.JSONDecodeError as e:
        return False, f"JSON mal formado: {e}"
    except ValidationError as e:
        return False, f"Estructura inválida: {e}"


def llamar_api_con_retry(messages, max_intentos=3):
    """
    Hace la llamada a la API con manejo de errores (try/except).
    Reintenta hasta max_intentos si hay errores de conexión/API.
    """
    for intento in range(max_intentos):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.1,
                max_tokens=200
            )
            return response

        except Exception as e:
            print(f"⚠️ Error en API (intento {intento + 1}/{max_intentos}): {e}")
            if intento == max_intentos - 1:
                raise  # Si falló el último intento, propagamos el error
            print("🔄 Reintentando...")


while True:
    user_input = input("👤 Vos: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        print("👋 ¡Hasta luego!")
        break

    history.append({"role": "user", "content": user_input})
    requiere_json = es_solicitud_de_datos(user_input)

    if requiere_json:
        print("📋 Detecté solicitud de datos. Validando con Pydantic...")

    try:
        # Llamada a API con manejo de errores y reintentos
        response = llamar_api_con_retry(history)
        respuesta_texto = response.choices[0].message.content

        if requiere_json:
            # Validación con Pydantic
            es_valido, resultado = validar_con_pydantic(respuesta_texto)

            if es_valido:
                print(f"✅ Datos validados con Pydantic:")
                print(json.dumps(resultado, indent=2, ensure_ascii=False))
                history.append({"role": "assistant", "content": respuesta_texto})

            else:
                # JSON inválido: pedimos corrección
                print(f"❌ Validación fallida: {resultado}")
                print(f"📝 Respuesta cruda: {respuesta_texto[:100]}...")
                print("🔄 Solicitando corrección...\n")

                # Agregamos mensaje de corrección al historial
                correccion = {
                    "role": "user",
                    "content": (
                        f"Error de validación: {resultado}\n"
                        f"Tu respuesta: {respuesta_texto}\n"
                        "Corregí y devolvé SOLO el JSON con: nombre (str), edad (int), email (str)"
                    )
                }
                history.append(correccion)

                # Reintentamos una vez
                response2 = llamar_api_con_retry(history)
                respuesta2 = response2.choices[0].message.content

                es_valido2, resultado2 = validar_con_pydantic(respuesta2)

                if es_valido2:
                    print(f"✅ Corrección exitosa:")
                    print(json.dumps(resultado2, indent=2, ensure_ascii=False))
                    history.append({"role": "assistant", "content": respuesta2})
                else:
                    print(f"❌ Corrección también falló: {resultado2}")
                    history.append({"role": "assistant", "content": respuesta2})

        else:
            # Respuesta normal
            print(f"🤖 IA: {respuesta_texto}\n")
            history.append({"role": "assistant", "content": respuesta_texto})

    except Exception as e:
        print(f"\n❌ Error fatal después de reintentos: {e}")
        print("El agente no pudo completar la solicitud.")
        continue

print("\n=== DESAFÍO COMPLETADO CON PYDANTIC ===")
print("Mejoras aplicadas:")
print("- ✅ Validación de tipos automática con Pydantic")
print("- ✅ Esquema definido: DatosUsuario(BaseModel)")
print("- ✅ Manejo de errores con try/except")
print("- ✅ Reintentos automáticos ante fallos de API")
