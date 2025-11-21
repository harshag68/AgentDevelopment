# agents/search_agent.py
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai import types

from manual_store_gcp import search_manuals, get_manual


def buscar_manuales_tool(text_query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Busca manuales por texto usando la tabla de diccionario (BigQuery).

    Args:
        text_query: Texto libre, por ejemplo "cargar cubo datos python".
        limit: Máximo de resultados a devolver (hoy lo ignora y deja que
               search_manuals aplique su propio límite interno).
    """
    # Si viene vacío, mandamos string vacío para que traiga "lo más reciente"
    results = search_manuals(text_query or "")

    print("\n[SEARCH_AGENT] Búsqueda de manuales:")
    print(f"  query: {text_query}")
    print(f"  encontrados: {len(results)}")
    for r in results:
        print(f"   - {r['manual_id']} | {r['title']} | {r.get('business_area', '-')}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "results": results,
    }


def obtener_manual_tool(manual_id: str) -> Dict[str, Any]:
    """
    Devuelve el detalle completo de un manual (metadatos + pasos + archivos).

    Args:
        manual_id: ID del manual, por ejemplo "MAN-1a2b3c4d".

    Returns:
        {
          "status": "ok",
          "manual": {...}
        }
        o
        {
          "status": "not_found",
          "manual_id": "MAN-xxxx"
        }
    """
    manual = get_manual(manual_id)
    if not manual:
        print(f"[SEARCH_AGENT] Manual no encontrado: {manual_id}")
        return {
            "status": "not_found",
            "manual_id": manual_id,
        }

    print(f"\n[SEARCH_AGENT] Manual encontrado: {manual_id} - {manual.get('title')}")
    print(f"  Area: {manual.get('business_area')}")
    print(f"  Steps: {len(manual.get('steps', []))}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "manual": manual,
    }


def create_search_agent(retry: types.HttpRetryOptions) -> LlmAgent:
    """
    Crea el agente especializado en:
    - Buscar manuales por texto.
    - Recuperar el detalle de un manual específico.
    """

    instruction = """
Eres el agente de BÚSQUEDA DE MANUALES.

Tu misión:
- Cuando el coordinador o el usuario necesiten encontrar un manual a partir de
  texto libre (tema, proceso, área, palabras clave), usa SIEMPRE el tool
  `buscar_manuales_tool(text_query=...)`.

- Cuando ya se tiene un `manual_id` y se requiere más detalle
  (pasos, archivos, contexto completo), usa el tool
  `obtener_manual_tool(manual_id=...)`.

Devuelve siempre:
- Una breve explicación de los resultados.
- Si hay varios manuales, lista los candidatos más relevantes con:
  manual_id, título, área de negocio y 2-3 palabras clave.
- Si abres el detalle de un manual, resume el contexto y lista los pasos principales.

NUNCA menciones que estás usando tools, otros agentes, ni detalles técnicos.
Habla al usuario como si fueras un solo asistente.
    """

    agent = LlmAgent(
        name="search_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[buscar_manuales_tool, obtener_manual_tool],
    )
    return agent
