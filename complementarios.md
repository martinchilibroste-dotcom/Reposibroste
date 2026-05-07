# 📚 Material Complementario: Ingeniería de Agentes de IA

Este documento contiene recursos adicionales para profundizar en los conceptos vistos en la Clase 2 y servir como guía de referencia durante el desarrollo de tus propios agentes autónomos.

---

## 📖 1. Glosario: Conceptos Clave

Para construir agentes, es fundamental dominar el lenguaje técnico del ecosistema:

* **LLM (Large Language Model):** El motor de inferencia que procesa y genera lenguaje.
* **Stateless (Sin Estado):** Propiedad de las APIs donde cada petición es independiente; la IA no "recuerda" nada si no le enviamos el historial completo en cada llamada.
* **Inferencia:** El proceso de generación de una salida basado en un input.
* **Hallucination (Alucinación):** Cuando el modelo genera información falsa con apariencia de verdad.
* **Temperature:** Parámetro que controla la aleatoriedad (0 = preciso/técnico, 1 = creativo).
* **Token:** La unidad mínima de procesamiento de texto (aprox. 4 caracteres).
* **Prompt Engineering:** El diseño de instrucciones para guiar el comportamiento del modelo.

---

## 🛠️ 2. Guía de Troubleshooting (Diagnóstico de Errores)

Si tu agente no se comporta como esperas, revisa estos puntos comunes:

### El Agente entra en un bucle infinito
* **Causa:** El `system_prompt` es ambiguo o el modelo no entiende la `Observation`.
* **Solución:** Verifica que estés agregando la `Observation` al historial de mensajes con el rol de `user` (o el que corresponda según el esquema ReAct) para que el modelo la procese.

### Error de JSON (JSONDecodeError)
* **Causa:** El modelo incluyó texto extra fuera del bloque JSON.
* **Solución:** Usa el **Structural Guard** o validación con **Pydantic** para limpiar y asegurar la estructura antes de procesarla.

### "Maximum context length reached"
* **Causa:** El historial de mensajes creció más allá del límite del modelo.
* **Solución:** Implementa una función de "poda" (pruning) que conserve solo los mensajes más recientes o resuma el historial antiguo.

---

## 📐 3. Ficha de Diseño: Mi Primer Agente Profesional

Utiliza este template antes de empezar a programar cualquier agente complejo:

- **1. Objetivo del Agente:** (Ej: "Asistente para analistas de riesgos financieros")
- **2. Modelo de Lenguaje:** (Ej: Llama-3-8B vía Groq o GPT-4o)
- **3. Inventario de Herramientas:**
    * `nombre_herramienta_1`: Descripción de uso y parámetros requeridos.
    * `nombre_herramienta_2`: Descripción de uso y parámetros requeridos.
- **4. Patrón de Razonamiento:** (¿Usará ReAct simple, Planner-Executor o Multi-Agente?)
- **5. Estructura de Memoria:** (¿Memoria volátil en lista de Python o persistente en base de datos?)

---

## 🗺️ 4. El Ecosistema de Frameworks

Una vez que domines la base manual de este curso, estos son los siguientes pasos en la industria:

| Framework | Enfoque Principal | Cuándo usarlo |
| :--- | :--- | :--- |
| **LangChain** | Integración y componentes | Para conectar herramientas y fuentes de datos rápidamente. |
| **CrewAI** | Orquestación Multi-Agente | Cuando necesitas que varios agentes especializados colaboren entre sí. |
| **AutoGen** | Conversaciones entre agentes | Para simulaciones complejas y flujos de trabajo basados en diálogo. |
| **MCP (Anthropic)** | Protocolo de Contexto | Para estandarizar cómo los modelos acceden a archivos y datos locales. |

---

## 🔐 5. Buenas Prácticas de Seguridad

* **Nunca** subas tu archivo `.env` a GitHub o repositorios públicos.
* Usa `gitignore` para excluir archivos con credenciales.
* Limita los créditos de tus API Keys para evitar gastos inesperados por bucles infinitos en el código.