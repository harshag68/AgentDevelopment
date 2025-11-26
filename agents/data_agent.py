# agents/data_agent.py
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai import types


from manual_store_gcp import search_manuals, get_manual, save_manual
from typing import Dict, Any, List


# ------------------------------------------------------------
# 1) TOOLS que usará el agente de datos
# ------------------------------------------------------------

def save_manual_tool(manual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a manual in the configured storage (GCP or local).

    - Accepts incomplete manuals (fields may be missing).
    - Normalizes the step structure to the format expected by manual_store_gcp.
    """
    print("\n[DATA_AGENT] >>> save_manual_tool called")
    print("[DATA_AGENT] title:", manual.get("title"))

    # Normalize keywords
    keywords = manual.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    manual["keywords"] = keywords

    # Normalize steps to the format expected by manual_store_gcp
    normalized_steps = []
    for idx, step in enumerate(manual.get("steps", []), start=1):
        normalized_steps.append(
            {
                "step_number": step.get("step_number", idx),
                "step_title": step.get("step_title") or step.get("title") or "",
                "step_description": step.get("step_description") or step.get("description") or "",
                "expected_output": step.get("expected_output") or "",
                "required_tools": step.get("required_tools") or "",
                # accept both "estimated_time" and "estimated_time_minutes"
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

    print("[DATA_AGENT] Manual saved/updated:")
    print(f"  ID:    {manual_id}")
    print(f"  Title: {stored.get('title')}")
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


def search_manuals_tool(text_query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Searches for manuals by text using the dictionary table (BigQuery).
    We ignore 'limit' because search_manuals already limits to 50.
    """
    results = search_manuals(text_query or "")

    print("\n[DATA_AGENT] Manual search:")
    print(f"  query: {text_query}")
    print(f"  found: {len(results)}")
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
      ...
    ]
  }

   - If information is missing, fill with empty strings or brief texts like
     "to be completed" instead of blocking.
   - The manual doesn't need to be perfect to save it.

2) You should ONLY call the `save_manual_tool(manual=...)` tool when
   it's clear the user wants to **SAVE** the manual. Typical signals:
   - "save"
   - "save it"
   - "let's leave it like this"
   - "that's good, save"
   - "create the manual"
   - "leave it saved"

   When you detect that in the conversation, build the best possible dictionary
   with available information and call `save_manual_tool`.

3) To search for manuals by text (for example to avoid duplicates or suggest an
   existing one), use the `search_manuals_tool(text_query=...)` tool.
   If one exists that's similar, tell them "manual 'x' exists with similar content."

IMPORTANT:
- Don't explain to the user that you're using tools or technical names.
- Your responses to the user should be brief and business-oriented, like:
  "Done, saved manual 'X' with N steps. We can improve it later if you want."
"""
    agent = LlmAgent(
        name="data_agent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[save_manual_tool, search_manuals_tool],
    )
    return agent
