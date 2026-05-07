"""
17_generator_evaluator_pipeline.py — Patrón Generador → Evaluador → Optimizador.

Arquitectura de dos modelos con roles distintos:

  ┌──────────────┐     respuesta     ┌──────────────┐
  │  GENERADOR   │ ────────────────► │  EVALUADOR   │
  │ (GEN_MODEL)  │                   │ (EVAL_MODEL) │
  │ llama 8b     │ ◄──── feedback ── │ llama 70b    │
  └──────────────┘    (si rechaza)   └──────────────┘

Flujo por intento:
  1. El Generador recibe la consulta y produce una respuesta (puede usar herramientas).
  2. El Evaluador audita la respuesta contra criterios de calidad y devuelve JSON.
  3a. Si aprueba  → se muestra la respuesta final al usuario. Fin.
  3b. Si rechaza  → el feedback se incorpora a la próxima consulta del Generador.
  4. Se repite hasta max_intentos. Si no pasa, se muestra la mejor respuesta lograda.

Por qué dos modelos distintos:
  - El Generador (8b) es rápido y barato: ideal para iterar.
  - El Evaluador (70b) es preciso: actúa como supervisor sin pagar su costo en cada token.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

import config2
from agent_runner2 import run_agent_silent
from tools import generar_informe_html

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

MAX_INTENTOS = 5


# ══════════════════════════════════════════════════════════════
# GENERADOR
# Responsabilidad: producir la mejor respuesta posible a la consulta.
# Puede usar herramientas (clima, descuento, búsqueda web).
# En cada reintento recibe el feedback del Evaluador incorporado.
# ══════════════════════════════════════════════════════════════
def generador(consulta: str) -> str:
    print(f"   ⚙️  [GENERADOR] Usando {config2.GEN_MODEL}...")
    return run_agent_silent(
        client=client,
        model=config2.GEN_MODEL,
        system_prompt=config2.GENERATOR_PROMPT,
        user_input=consulta
    )


# ══════════════════════════════════════════════════════════════
# EVALUADOR
# Responsabilidad: auditar la respuesta del Generador.
# Usa JSON mode para garantizar una salida estructurada y parseable.
# No usa herramientas: solo razona sobre el texto que recibe.
# ══════════════════════════════════════════════════════════════
def evaluador(consulta_original: str, respuesta_agente: str) -> dict:
    print(f"   🔍 [EVALUADOR] Auditando con {config2.EVAL_MODEL}...")

    # Inyectamos la consulta y la respuesta dentro del prompt del evaluador
    prompt_completo = f"""{config2.EVALUATOR_PROMPT}

CONSULTA ORIGINAL DEL USUARIO:
{consulta_original}

RESPUESTA DEL AGENTE A EVALUAR:
{respuesta_agente}
"""

    response = client.chat.completions.create(
        model=config2.EVAL_MODEL,
        messages=[{"role": "system", "content": prompt_completo}],
        # JSON mode: fuerza al modelo a devolver JSON válido.
        # Evita que json.loads() rompa por texto extra alrededor del objeto.
        response_format={"type": "json_object"},
        temperature=0   # Temperatura 0: queremos juicio determinista, no creativo
    )

    return json.loads(response.choices[0].message.content)


# ══════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# Orquesta los ciclos de generación → evaluación → optimización.
# ══════════════════════════════════════════════════════════════
def pipeline(consulta_inicial: str) -> None:
    consulta_actual = consulta_inicial
    mejor_respuesta = None
    mejor_puntaje   = 0

    for intento in range(1, MAX_INTENTOS + 1):
        print(f"\n{'─'*55}")
        print(f"🚀 INTENTO {intento} de {MAX_INTENTOS}")
        print(f"{'─'*55}")

        # ── Paso 1: Generación ──
        respuesta = generador(consulta_actual)

        # ── Paso 2: Evaluación ──
        auditoria = evaluador(consulta_inicial, respuesta)

        puntaje    = auditoria.get("puntaje", 0)
        aprobado   = auditoria.get("aprobado", False)
        feedback   = auditoria.get("feedback", "")
        sugerencia = auditoria.get("sugerencia", "")

        # Guardamos la mejor respuesta aunque no llegue a aprobarse
        if puntaje > mejor_puntaje:
            mejor_puntaje   = puntaje
            mejor_respuesta = respuesta

        if aprobado:
            print(f"\n✅ [CONTROL DE CALIDAD] APROBADO — Puntaje: {puntaje}/10")
            print(f"\n{'═'*55}")
            print("🤖 RESPUESTA FINAL APROBADA:")
            print(f"{'═'*55}")
            print(respuesta)
            ofrecer_informe(consulta_inicial, respuesta)
            return

        # ── Paso 3: Optimización — preparamos el siguiente intento ──
        print(f"\n❌ [CONTROL DE CALIDAD] RECHAZADO — Puntaje: {puntaje}/10")
        print(f"   📝 Feedback:   {feedback}")
        print(f"   💡 Sugerencia: {sugerencia}")

        if intento < MAX_INTENTOS:
            # El feedback del evaluador se convierte en instrucción para el generador.
            # Este es el corazón del patrón Optimizador: el error de un ciclo
            # alimenta la mejora del siguiente.
            consulta_actual = (
                f"Consulta original: {consulta_inicial}\n\n"
                f"Tu respuesta anterior fue rechazada por el auditor de calidad.\n"
                f"Feedback recibido: {feedback}\n"
                f"Qué debés mejorar: {sugerencia}\n\n"
                f"Generá una nueva respuesta corrigiendo estos puntos."
            )

    # Si se agotaron los intentos, mostramos la mejor respuesta obtenida
    print(f"\n⚠️  Se alcanzó el límite de {MAX_INTENTOS} intentos.")
    print(f"   Mejor puntaje logrado: {mejor_puntaje}/10")
    print(f"\n{'═'*55}")
    print("🤖 MEJOR RESPUESTA OBTENIDA:")
    print(f"{'═'*55}")
    print(mejor_respuesta)
    ofrecer_informe(consulta_inicial, mejor_respuesta)


# ══════════════════════════════════════════════════════════════
# OFERTA DE INFORME HTML — versión conversacional
#
# En lugar de preguntar "s/n", el pipeline hace una pregunta
# abierta y usa un LLM pequeño para interpretar la respuesta
# en lenguaje natural. El modelo:
#   - Detecta si el usuario quiere o no el informe HTML.
#   - Sugiere un nombre de archivo basado en el contenido.
#   - Acepta nombres que el usuario indique libremente.
#   - Devuelve JSON estructurado para que el pipeline actúe.
#
# Esto ilustra cómo un LLM puede reemplazar lógica de parseo
# frágil (if "s" / elif "no") con comprensión semántica real.
# ══════════════════════════════════════════════════════════════
def ofrecer_informe(consulta: str, respuesta: str) -> None:
    print(f"\n{'─'*55}")
    user_input = input("📄 ¿Querés que genere un informe HTML con esta respuesta? ").strip()

    if not user_input:
        return

    # El LLM interpreta la respuesta libre del usuario
    prompt_contexto = f"""{config2.HTML_ASSISTANT_PROMPT}

TÍTULO SUGERIDO BASADO EN LA CONSULTA: {consulta[:80]}
RESPUESTA DEL AGENTE (primeras 200 chars): {respuesta[:200]}...

RESPUESTA DEL USUARIO: {user_input}
"""

    decision_raw = client.chat.completions.create(
        model=config2.EVAL_MODEL,
        messages=[{"role": "system", "content": prompt_contexto}],
        response_format={"type": "json_object"},
        temperature=0
    )

    decision = json.loads(decision_raw.choices[0].message.content)

    # Mostramos el mensaje natural del asistente
    print(f"   🤖 {decision.get('mensaje', '')}")

    if not decision.get("generar", False):
        return

    titulo = consulta[:80] if len(consulta) > 80 else consulta
    nombre_archivo = decision.get("nombre_archivo", "")

    print("   Generando informe HTML...")
    resultado = json.loads(generar_informe_html(titulo=titulo, contenido=respuesta, nombre_archivo=nombre_archivo))

    if "error" in resultado:
        print(f"   ❌ Error: {resultado['error']}")
    else:
        print(f"   ✅ Informe HTML guardado en: {resultado['archivo']}")


def main():
    print("🤖 Pipeline Generador-Evaluador iniciado.\n")

    consulta = input("👤 Ingresá tu consulta: ").strip()
    if not consulta:
        consulta = "Explicame qué es un decorador en Python usando una analogía de una pizzería."
        print(f"(Usando consulta de ejemplo: '{consulta}')\n")

    pipeline(consulta)


if __name__ == "__main__":
    main()
