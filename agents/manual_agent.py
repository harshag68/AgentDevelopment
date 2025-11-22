# agents/manual_agent.py
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from manual_store_gcp import search_manuals, get_manual, save_manual
from typing import Dict, Any, List


def save_manual_tool(manual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a manual in the configured storage (GCP).

    - Accepts incomplete manuals (fields may be missing).
    - Normalizes the step structure to the format expected by manual_store_gcp.
    """
    print("\n[MANUAL_AGENT] >>> save_manual_tool called")
    print("[MANUAL_AGENT] title:", manual.get("title"))

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

    print("[MANUAL_AGENT] Manual saved/updated:")
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

    print("\n[MANUAL_AGENT] Manual search:")
    print(f"  query: {text_query}")
    print(f"  found: {len(results)}")
    for r in results:
        print(f"   - {r['manual_id']} | {r['title']} | {r.get('business_area', '-')}")
    print("-------------------------------------------------\n")

    return {
        "status": "ok",
        "results": results,
    }

   Once you have enough context, generate a manual in Markdown format, ALWAYS with this structure:

   # {Manual Title}

   ## 1. Context and Objective
   - Area / team: ...
   - Objective: ...
   - When to use: ...
   - Scope: ...

   ## 2. Prerequisites
   - Required permissions and access
   - Required systems or tools
   - Information or data needed before starting

   ## 3. Step-by-Step Procedure
   Numbered list with clear steps. Each step includes:
   - Concrete action
   - Who performs it (role)
   - Important notes or tips if applicable

   ## 4. Deliverables and Success Criteria
   - What's ready when finished
   - How to validate the process was done correctly

   ## 5. Quick Checklist for User
   A list of 5–10 short items the user can review
   to verify nothing was skipped.

   ## 6. Keywords (tags)
   A list of comma-separated tags that allow classifying the manual.
   Example: `onboarding, technology, data analysts, system access`

3) **Manual Updates**
   - Refer to the manual by title, not by ID.
   - If the user wants to MODIFY or UPDATE a manual,
     first ask them to indicate what part changed (requirements, steps, deliverables, etc.)
   - Then propose a new version of the corresponding fragment while maintaining the format.

4) You should ONLY call the `save_manual_tool(manual=...)` tool when
   it's clear the user wants to **SAVE** the manual. Typical signals:
   - "save"
   - "save it"
   - "let's leave it like this"
   - "that's good, save"
   - "create the manual"
   - "leave it saved"

   When you detect that in the conversation, build the best possible dictionary
   with available information and call `save_manual_tool`.

Style:
- Clear language, professional but friendly.
- Don't invent critical data (permissions, systems) if the user didn't provide them.
  In those cases, explicitly tell them what's missing and ask.

IMPORTANT:
- DO NOT say you save manuals on your own.
- When the user wants to **save / generate document**, simply say it in the response,
  the backend will handle persisting it.
"""

    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
        name="manual_agent",
        description=(
            "Agent specialized in creating, structuring, and updating internal manuals "
            "based on conversations with collaborators."
        ),
        instruction=instruction,
        tools=[save_manual_tool, search_manuals_tool],
    )

    return agent
