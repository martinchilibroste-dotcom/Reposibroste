# Alternativas a OpenAI para Desarrollo de Agentes

---

## 🚀 1. Groq (La mejor para Agentes)

Es, por lejos, la opción más rápida del mercado. Para agentes que tienen que "pensar" (razonar) varias veces antes de responder, la velocidad de Groq es una ventaja injusta.

- **Modelos**: Llama 3 (8B, 70B), Mixtral, Gemma.
- **Costo**: Tiene un "Free Tier" muy generoso para experimentación.

**Sintaxis en Python:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="TU_API_KEY_DE_GROQ"
)
# El resto del código es IDENTICO
```

---

## 🌐 2. OpenRouter (El "Supermercado" de modelos)

OpenRouter es un agregador. Lo mejor es que tienen una categoría específica de Modelos Gratis.

- **Modelos**: Van rotando, pero suelen tener Llama 3 Free, Mistral Free, y modelos de Qwen.
- **Ventaja**: Si un modelo gratis cae, solo cambiás el nombre del modelo en el código y listo.

**Configuración:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="TU_API_KEY_DE_OPENROUTER"
)
# Usás el modelo: "openrouter/free" o uno específico como "meta-llama/llama-3-8b-instruct:free"
```

---

## 🐙 3. GitHub Models (Ideal para Prototipado)

Si tus alumnos tienen cuenta de GitHub, ya tienen acceso a modelos de "primera línea" gratis (GPT-4o, Llama 3.1 405B, etc.) para pruebas.

- **Limitación**: Solo para uso personal/prototipos, no para producción. Tiene límites de tokens por minuto más estrictos.
- **Configuración**: Se usa a través del endpoint de Azure/GitHub.

---

## 🏠 4. Ollama (Local y 100% Ilimitado)

Si el alumno tiene una buena compu (especialmente con placa NVIDIA o Mac M1/M2/M3), esta es la mejor opción: correr el modelo en su propia máquina.

- **Costo**: $0 para siempre. Sin límites de API.
- **Setup**: Instalan Ollama, corren `ollama run llama3` y listo.

**Código:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Se pone cualquier cosa, no se usa
)
```
