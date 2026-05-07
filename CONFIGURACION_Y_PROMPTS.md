# Configuración externa y diseño de prompts

## 1. ¿Por qué separar la configuración en un archivo aparte?

Tener `MODEL` y `SYSTEM_PROMPT` en `config.py` en lugar de hardcodearlos en el código principal tiene ventajas concretas:

### Separación de responsabilidades
El código (`14_agente_pro.py`) se ocupa de **cómo funciona** el agente. El archivo de configuración (`config.py`) define **cómo se comporta**. Son dos preguntas distintas que no deberían mezclarse en el mismo lugar.

### Modificación sin tocar el código
Para cambiar el modelo o ajustar las instrucciones del agente, solo editás `config.py`. No tenés que buscar dentro de la lógica del programa, ni arriesgarte a romper algo por accidente.

### Hot-reload
Gracias al `importlib.reload(config)` al inicio de cada sesión, los cambios en `config.py` se reflejan en la próxima ejecución **sin necesidad de reiniciar nada más**.

### Colaboración
Un instructor, diseñador instruccional o product manager puede editar el prompt en `config.py` sin necesitar entender Python. El desarrollador y el diseñador del agente pueden trabajar en paralelo sin pisarse.

### Escalabilidad
Si el proyecto crece, podés tener múltiples configuraciones: `config_produccion.py`, `config_testing.py`, `config_cliente_A.py`, y cambiar entre ellas con una sola línea de importación.

---

## 2. El patrón C-R-I-S-E para diseñar system prompts

Un prompt mal estructurado produce respuestas inconsistentes, demasiado largas, fuera de tono o directamente incorrectas. El patrón **C-R-I-S-E** es un framework para escribir prompts que guían al modelo de forma precisa y predecible.

### C — Contexto
> *¿Quién está del otro lado? ¿En qué situación se encuentra?*

Le da al modelo información sobre el **usuario** y el **entorno**. Sin contexto, el modelo asume un usuario genérico y puede ser demasiado básico o demasiado avanzado.

```
* Contexto: Tienes a un usuario del otro lado que busca resolver dudas
generales y aprender cosas nuevas.
```

### R — Rol
> *¿Quién sos vos (el modelo) en esta conversación?*

Define la **identidad y autoridad** del asistente. Un modelo que sabe que actúa como "mentor paciente" ajusta su tono, nivel de detalle y paciencia de forma diferente a uno que actúa como "asistente genérico".

```
* Rol: Actúa como un experto consultor y un mentor paciente.
```

### I — Instrucción
> *¿Qué tenés que hacer exactamente?*

Es el corazón del prompt. Define la **tarea concreta** y cómo abordarla. Cuanto más específica, mejor.

```
* Instrucción: Analiza la petición del usuario y responde yendo directo al
grano pero asegurándote de que el concepto principal se entienda paso a paso.
```

### S — Salida
> *¿En qué formato debe venir la respuesta?*

Los LLMs pueden responder en prosa, listas, tablas, JSON, Markdown, etc. Si no se especifica, el modelo elige por su cuenta y el resultado es inconsistente. Definir el formato de salida garantiza **respuestas predecibles y uniformes**.

```
* Salida: Estructura toda tu respuesta utilizando formato Markdown.
Si presentas pasos, usa viñetas numeradas. Si compartes código, usa bloques
de código con el resaltado correcto.
```

### E — Ejemplo (y Restricciones)
> *¿Qué debe y qué NO debe hacer?*

Los ejemplos concretos (**few-shot prompting**) anclan el tono y estilo mejor que cualquier descripción abstracta. Las prohibiciones explícitas eliminan los vicios más comunes de los LLMs.

```
* Prohibición: No uses lenguaje robótico, no des introducciones excesivamente
largas y, sobre todo, no inventes información.

* Ejemplo: [Usuario]: '¿Qué es una API?'
[Tú]: 'Piensa en una API como el mesero de un restaurante...'
```

---

## Resumen

| Componente | Pregunta clave | Efecto |
|---|---|---|
| **Contexto** | ¿Quién es el usuario? | Ajusta nivel y tono |
| **Rol** | ¿Quién soy yo? | Define identidad y autoridad |
| **Instrucción** | ¿Qué debo hacer? | Guía la tarea concreta |
| **Salida** | ¿Cómo debe verse la respuesta? | Garantiza formato consistente |
| **Ejemplo** | ¿Qué debo/no debo hacer? | Ancla estilo y elimina vicios |

Un prompt estructurado con C-R-I-S-E no es más largo que uno mal escrito; es más **preciso**. La diferencia está en que cada línea cumple una función específica y el modelo tiene menos ambigüedad para resolver por su cuenta.
