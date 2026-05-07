import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar configuración
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"  # O el que prefieras usar


def main():
    # 2. Inicializar memoria (State)
    messages = [
        {"role": "system", "content": "Sos un asistente técnico experto."}
    ]

    print("🤖 Agente inicializado. Escribí 'salir' para terminar.")

    while True:
        # 3. Captura de entrada
        user_input = input("\n👤 Vos: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break

        # 4. Actualizar historial
        messages.append({"role": "user", "content": user_input})

        try:
            # 5. Llamada a la API
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )

            # 6. Procesar respuesta
            answer = response.choices[0].message.content
            print(f"\n🤖 IA: {answer}")

            # 7. Persistir en memoria
            messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
