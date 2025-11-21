# agents/manual_agent.py
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from manual_store_gcp import search_manuals, get_manual, save_manual
from typing import Dict, Any, List
def guardar_manual_tool(manual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarda o actualiza un manual en el storage configurado (GCP).

    - Acepta manuales incompletos (pueden faltar campos).
    - Normaliza la estructura de pasos al formato esperado por manual_store_gcp.
    """
    print("\n[DATA_AGENT] >>> guardar_manual_tool llamado")
    print("[DATA_AGENT] título:", manual.get("title"))

    # Normalizar keywords
    keywords = manual.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    manual["keywords"] = keywords

    # Normalizar pasos al formato esperado por manual_store_gcp
    normalized_steps = []
    for idx, step in enumerate(manual.get("steps", []), start=1):
        normalized_steps.append(
            {
                "step_number": step.get("step_number", idx),
                "step_title": step.get("step_title") or step.get("title") or "",
                "step_description": step.get("step_description") or step.get("description") or "",
                "expected_output": step.get("expected_output") or "",
                "required_tools": step.get("required_tools") or "",
                # aceptamos tanto "estimated_time" como "estimated_time_minutes"
                "estimated_time": step.get("estimated_time")
                                 or step.get("estimated_time_minutes")
                                 or "",
                "is_critical": bool(step.get("is_critical")),
            }
        )
    manual["steps"] = normalized_steps

    saved = save_manual(manual)
    manual_id = saved.get("manual_id")

    stored = get_manual(manual_id)

    print("[DATA_AGENT] Manual guardado/actualizado:")
    print(f"  ID:    {manual_id}")
    print(f"  Título:{stored.get('title')}")
    print(f"  Steps: {len(stored.get('steps', []))}")
    print("-------------------------------------------------\n")

    file_path = None
    files = stored.get("files", [])
    if files:
        file_path = files[0].get("file_path")

    return {
        "status": "ok",
        "manual_id": manual_id,
        "title": stored.get("title"),
        "file_path": file_path,
        "steps_count": len(stored.get("steps", [])),
    }


def buscar_manuales_tool(text_query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Busca manuales por texto usando la tabla de diccionario (BigQuery).
    Ignoramos 'limit' porque search_manuals ya limita a 50.
    """
    results = search_manuals(text_query or "")

    print("\n[DATA/DATA_AGENT] Búsqueda de manuales:")
    print(f"  query: {text_query}")
    print(f"  encontrados: {len(results)}")
    for r in results:
        print(f"   - {r['manual_id']} | {r['title']} | {r.get('business_area', '-')}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "results": results,
    }
def create_manual_agent(retry: types.HttpRetryOptions) -> LlmAgent:
    """
    Agente especialista en CREAR y ACTUALIZAR manuales internos.

    Rol:
    - Pedir contexto del manual (diccionario de manuales).
    - Guiar al usuario paso a paso.
    - Generar un manual bien estructurado en formato Markdown.
    """

    instruction = """
Eres un **Agente de Manuales Internos** para una empresa.

SIEMPRE RESPONDES EN ESPAÑOL.

Tu trabajo principal es:

1) **Levantar el diccionario del manual** (metadatos)
   Idealmente debes solicitar más información SOLO si el usuario NO ha pedido guardar.
   - Título del manual.
   - Área / Gerencia / Equipo que lo pide.
   - Para qué sirve (objetivo del manual).
   - Cuándo se usa (disparadores, frecuencia, escenarios típicos).
   - Requisitos previos (permisos, accesos, sistemas, datos, roles mínimos).
   - Entregables o resultado final (qué queda listo al terminar el proceso).
   - Personas involucradas (roles clave).
   - Riesgos o errores típicos que se deben evitar (si aplica).
PERFECTO: Si el usuario dice "guarda", "listo", "crea el manual", "guárdalo", "dejémoslo así", 
NO debes pedir más información aunque falte. 
Debes asumir valores razonables o dejar "por completar" y proceder a guardar.

2) **Construir el manual paso a paso**
   Una vez que tengas suficiente contexto, genera un manual en formato Markdown, SIEMPRE con esta estructura:

   # {Título del manual}

   ## 1. Contexto y objetivo
   - Área / equipo: ...
   - Objetivo: ...
   - Cuándo se usa: ...
   - Alcance: ...

   ## 2. Requisitos previos
   - Permisos y accesos necesarios
   - Sistemas o herramientas requeridas
   - Información o datos que se deben tener antes de empezar

   ## 3. Paso a paso del procedimiento
   Lista numerada con pasos claros. Cada paso incluye:
   - Acción concreta
   - Quién lo realiza (rol)
   - Notas o tips importantes si aplica

   ## 4. Entregables y criterios de éxito
   - Qué queda listo al finalizar
   - Cómo se valida que el proceso quedó bien hecho

   ## 5. Checklist rápida para el usuario
   Una lista de 5–10 ítems cortos que el usuario puede revisar
   para verificar que no se saltó nada.

   ## 6. Palabras clave (tags)
   Una lista de tags separadas por coma que permitan clasificar el manual.
   Ejemplo: `onboarding, tecnología, analistas de datos, acceso sistemas`

3) **Actualización de manuales**
    - Refierete al manual por el titulo no por el id,
   - Si el usuario dice que quiere MODIFICAR o ACTUALIZAR un manual,
     primero pide que te indique qué parte cambió (requisitos, pasos, entregables, etc.)
   - Luego propone una versión nueva del fragmento correspondiente manteniendo el formato.

   2) SOLO debes llamar al tool `guardar_manual_tool(manual=...)` cuando
   quede claro que el usuario quiere **GUARDAR** el manual. Señales típicas:
   - "guarda"
   - "guárdalo"
   - "dejémoslo así"
   - "así está bien, guarda"
   - "crea el manual"
   - "déjalo guardado"

   Cuando detectes eso en la conversación, arma el mejor diccionario posible
   con la información disponible y llama a `guardar_manual_tool`.

Estilo:
- Lenguaje claro, profesional pero cercano.
- No inventes datos críticos (permisos, sistemas) si el usuario no los dio.
  En esos casos explícitamente dile que faltan y pregunta.

IMPORTANTE:
- NO digas que guardas manuales por tu cuenta.
- Cuando el usuario quiera **guardar / generar documento**, simplemente dilo en la respuesta,
  el backend se encargará de persistirlo.
"""

    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
        name="manual_agent",
        description=(
            "Agente especializado en crear, estructurar y actualizar manuales internos "
            "a partir de conversaciones con colaboradores."
        ),
        instruction=instruction,
        tools=[guardar_manual_tool, buscar_manuales_tool],
        
    )

    return agent
