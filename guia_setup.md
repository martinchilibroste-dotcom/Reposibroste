# 🛠️ Guía de Setup: Entorno para Ingeniería de Agentes

Esta guía asegura que todos los alumnos tengan exactamente el mismo entorno, minimizando errores de "en mi máquina no funciona".

---

## 1. Requisitos Previos

- **Python 3.10 o superior**: (Importante para el soporte de type hinting avanzado y librerías de IA).
- **Editor**: VS Code (recomendado) o PyCharm.

---

## 2. Creación del Entorno Virtual (VENV)

En la terminal de la carpeta del proyecto, los alumnos deben ejecutar:

```bash
# Crear el entorno
python -m venv venv

# Activarlo (Windows)
.\venv\Scripts\activate

# Activarlo (Mac/Linux)
source venv/bin/activate
```

---

## 3. Instalación de Librerías Base

Creamos un archivo llamado `requirements.txt` con lo mínimo indispensable para empezar:

```
python-dotenv
openai
pydantic
tiktoken
psutil
```

Y luego instalan todo de una:

```bash
pip install -r requirements.txt
```

---

## 🚀 El "Starter Code" (Chat Loop Base)

Este es el archivo `app.py` que podés darles para que todos empiecen desde el mismo punto. Es un código limpio, sin "magia", para que ellos lo completen durante la clase.

```python
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
```
