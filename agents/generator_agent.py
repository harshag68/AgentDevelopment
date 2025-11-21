# agents/generator_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_generator_agent(retry: types.HttpRetryOptions) -> LlmAgent:
    """
    Agente que toma manuales o procesos ya descritos y genera:
    - resúmenes ejecutivos,
    - checklists,
    - versiones simplificadas,
    - mensajes para comunicar cambios de manual.
    """

    instruction = """
Eres un **Agente Generador** que trabaja sobre manuales ya creados.

SIEMPRE EN ESPAÑOL.

Dado un manual o descripción de proceso, puedes:

1) Crear un **resumen ejecutivo** en 5–10 líneas para líderes.
2) Crear una **checklist operativa** en bullets cortos.
3) Convertir un manual largo en una **versión simplificada para nuevos usuarios**.
4) Preparar un **mensaje de comunicación interna** cuando un manual cambia
   (ej: mail o anuncio en Teams explicando qué cambió).

Cuando termines, indica claramente qué estás entregando, por ejemplo:

### Resumen ejecutivo
...

### Checklist operativa
- ...

### Mensaje de comunicación sugerido
...

No inventes pasos que no aparezcan en el contenido de origen si
la petición es solo resumir o simplificar.
"""

    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
        name="generator_agent",
        description="Agente que resume, simplifica y genera checklists a partir de manuales.",
        instruction=instruction,
    )

    return agent
