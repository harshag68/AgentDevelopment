# agents/coordinator.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_coordinator(
    manual_agent,
    data_agent,
- If the user asks for a **summary**, a checklist, or a short version:
  -> Use `generator_agent` but call it Emilio (Generator Agent).

Response format:

- Your final output to the user should be clear and readable. You can use Markdown:
  - Headers (`#`, `##`)
  - Lists
  - Checklists (`- [ ] ...`)

- If you call sub-agents, integrate their responses into a single coherent message.
- Avoid showing the user technical details of the sub-agents, only the useful result without any mention of the agents.
- If they say save at any time, you must call the data_agent to save to GCP the manual as is.
Examples of things you can do:
- Guide a conversation to create a new manual from scratch.
- Take an existing manual and return summary + checklist.
- Propose how the tables in BigQuery would look to store that manual.
"""

    coordinator = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
        name="coordinator",
        description="Coordinator agent that decides how to use the manual sub-agents.",
        instruction=instruction,
        sub_agents=[manual_agent, data_agent, search_agent, generator_agent],
    )

    return coordinator
