# agents/search_agent.py
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai import types

from manual_store_gcp import search_manuals, get_manual


def search_manuals_tool(text_query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Searches for manuals by text using the dictionary table (BigQuery).

    Args:
        text_query: Free text, for example "load data cube python".
        limit: Maximum results to return (currently ignored, lets
               search_manuals apply its own internal limit).
    """
    # If empty, send empty string to get "most recent"
    results = search_manuals(text_query or "")

    print("\n[SEARCH_AGENT] Manual search:")
    print(f"  query: {text_query}")
    print(f"  found: {len(results)}")
    for r in results:
        print(f"   - {r['manual_id']} | {r['title']} | {r.get('business_area', '-')}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "results": results,
    }


def get_manual_tool(manual_id: str) -> Dict[str, Any]:
    """
    Returns the complete detail of a manual (metadata + steps + files).

    Args:
        manual_id: Manual ID, for example "MAN-1a2b3c4d".

    Returns:
        {
          "status": "ok",
          "manual": {...}
        }
        or
        {
          "status": "not_found",
          "manual_id": "MAN-xxxx"
        }
    """
    manual = get_manual(manual_id)
    if not manual:
        print(f"[SEARCH_AGENT] Manual not found: {manual_id}")
        return {
            "status": "not_found",
            "manual_id": manual_id,
        }

    print(f"\n[SEARCH_AGENT] Manual found: {manual_id} - {manual.get('title')}")
    print(f"  Area: {manual.get('business_area')}")
    print(f"  Steps: {len(manual.get('steps', []))}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "manual": manual,
    }

    )
    return agent
