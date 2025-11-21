# agents/data_agent.py
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai import types


from manual_store_gcp import search_manuals, get_manual, save_manual
from typing import Dict, Any, List


# ------------------------------------------------------------
# 1) TOOLS que usará el agente de datos
# ------------------------------------------------------------

def guardar_manual_tool(manual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarda o actualiza un manual en el storage configurado (GCP o local).

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



# ------------------------------------------------------------
# 2) Crear agente de datos
# ------------------------------------------------------------

def create_data_agent(retry: types.HttpRetryOptions) -> LlmAgent:
    """
    Crea el agente encargado de:
    - Recibir manuales ya descritos (texto libre o Markdown).
    - Convertirlos en un diccionario estructurado.
    - LLAMAR A guardar_manual_tool SOLO CUANDO EL USUARIO PIDA GUARDAR.
    - Usar buscar_manuales_tool cuando necesite encontrar manuales por contexto.
    """

    instruction = """
Eres el **agente de DATOS** de manuales.

SIEMPRE RESPONDES EN ESPAÑOL AL USUARIO (a través del coordinador), 
pero internamente puedes usar herramientas.

Tu trabajo:

1) Recibir información de un manual (puede venir en texto libre o Markdown)
   desde otros agentes / el coordinador y convertirla en un diccionario
   con esta forma base (los campos pueden venir incompletos, no pasa nada):

  {
    "title": "...",
    "business_area": "...",
    "requester": "...",
    "created_by": "...",
    "context": "...",
    "requirements": "...",
    "permissions": "...",
    "outputs": "...",
    "keywords": ["palabra1", "palabra2"],
    "steps": [
      {
        "step_title": "...",
        "step_description": "...",
        "expected_output": "...",
        "required_tools": "...",
        "estimated_time": "10 minutos",
        "is_critical": true
      },
      ...
    ]
  }

   - Si falta información, rellena con cadenas vacías o textos breves como
     "por completar" en vez de bloquearte.
   - No es necesario que el manual esté perfecto para guardarlo.

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

3) Para buscar manuales por texto (por ejemplo para no duplicar o sugerir uno
   existente), usa el tool `buscar_manuales_tool(text_query=...)`.
   Si existe uno que se asemeje le dices, existe el manual "x" con contenido similar.

IMPORTANTE:
- No expliques al usuario que estás usando tools ni nombres técnicos.
- Tus respuestas hacia el usuario deben ser breves y orientadas a negocio, del tipo:
  "Listo, dejé guardado el manual 'X' con N pasos. Si quieres luego lo podemos mejorar."
"""
    agent = LlmAgent(
        name="data_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[guardar_manual_tool, buscar_manuales_tool],
    )
    return agent
