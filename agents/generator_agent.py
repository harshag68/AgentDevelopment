# agents/generator_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_generator_agent(retry: types.HttpRetryOptions) -> LlmAgent:
### Operational Checklist
- ...

### Suggested Communication Message
...

Don't invent steps that don't appear in the source content if
the request is only to summarize or simplify.
"""

    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry),
        name="generator_agent",
        description="Agent that summarizes, simplifies, and generates checklists from manuals.",
        instruction=instruction,
    )

    return agent
