# Patrón ReAct: Reasoning + Acting

ReAct es un patrón de prompting que combina **Razonamiento** (Thought) y **Acción** (Action) en un ciclo iterativo. El modelo piensa, actúa, observa el resultado, y repite hasta resolver la tarea.

En términos prácticos, como estamos viendo en el desarrollo de la Clase 2, este patrón se implementa mediante un System Prompt estricto que prohíbe a la IA responder directamente al usuario hasta que haya completado satisfactoriamente este ciclo de razonamiento y acción.

## ¿Por qué funciona?

- Permite al modelo acceder a información externa (herramientas/APIs)
- Obliga a un razonamiento paso a paso (chain-of-thought)
- Cada observación informa el siguiente razonamiento

## El Ciclo ReAct

```
Thought → Action → Observation → (repeat) → Final Answer
```

## Formato de Respuesta Obligatorio

```text
Thought: [Razonamiento interno del modelo sobre qué necesita hacer]
Action: [Comando técnico de la herramienta, ej: buscar_web("Python historia")]
Observation: [Resultado REAL que devuelve la herramienta]
... (bucle se repite hasta tener suficiente información) ...
Final Answer: [Respuesta final al usuario]
```

## System Prompt ReAct

```text
Sos un Agente de Investigación Autónomo. Tu objetivo es resolver la consulta del usuario.
NO respondas directamente. Debés seguir ESTRICTAMENTE este formato para cada paso:

Thought: [Explicá tu razonamiento técnico y planificá el siguiente paso]
Action: [Escribí el comando de herramienta disponible]
Observation: [Esperarás que Python te devuelva el resultado real aquí]

Solo cuando tengas la información completa, terminá con:
Final Answer: [Tu respuesta final para el usuario]

Herramientas disponibles:
- buscar_web(query) → Devuelve resumen de resultados de búsqueda
- consultar_basedatos(tabla, clave) → Devuelve JSON con datos
```

## Ejemplo Práctico Completo

**Consulta del usuario**: "¿Cuál es la población actual de Buenos Aires y cuánto creció desde 2010?"

```
Thought: Necesito buscar la población actual de Buenos Aires y la de 2010 para calcular el crecimiento.
Action: buscar_web("población Buenos Aires 2024")
Observation: Según INDEC 2024, CABA tiene 3,120,000 habitantes.

Thought: Ahora necesito la población de 2010 para comparar.
Action: buscar_web("población Buenos Aires censo 2010")
Observation: Censo 2010: 2,890,000 habitantes.

Thought: Tengo ambos datos. Crecimiento = 3,120,000 - 2,890,000 = 230,000. Porcentaje = 230,000/2,890,000 * 100 ≈ 7.96%
Final Answer: La población de Buenos Aires es 3,120,000 habitantes (2024), creció 230,000 personas (≈8%) desde 2010.