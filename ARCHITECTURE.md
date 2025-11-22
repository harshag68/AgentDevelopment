# 🏗️ Architecture: Manuel El Manual

This document explains the high-level architecture and component interactions of the "Manuel El Manual" application.

## 🔄 High-Level Flow

1.  **User Interaction**: The user speaks or types a question in the web interface (`index.html`).
2.  **API Request**: The frontend sends a POST request to `/ask` on the FastAPI server (`main.py`).
3.  **Agent Coordination**:
    *   The server receives the request and passes it to the **Coordinator Agent** (Manuel).
    *   The Coordinator decides which sub-agent is best suited to handle the request:
        *   **Manual Agent**: For creating/editing manuals.
        *   **Data Agent**: For saving manuals to the database.
        *   **Search Agent**: For finding existing manuals.
        *   **Generator Agent**: For creating summaries/checklists.
4.  **Agent Execution**:
    *   The selected agent processes the request, potentially using **Tools** (e.g., `search_manuals_tool`, `save_manual_tool`).
    *   These tools interact with **Google Cloud Platform** (BigQuery for metadata, Cloud Storage for content).
5.  **Response**: The agent generates a text response, which is sent back to the frontend and displayed (or spoken) to the user.

## 🧩 Component Deep Dive

### 1. Frontend (`index.html`)
*   **Technology**: Vanilla HTML, CSS, JavaScript.
*   **Role**: User interface for chat and voice interaction.
*   **Key Features**:
    *   **Voice Recognition**: Uses the Web Speech API to convert speech to text.
    *   **Text-to-Speech**: Reads the agent's responses aloud.
    *   **Chat Interface**: Displays the conversation history.
    *   **Manual Viewer**: A modal to display the full content of retrieved manuals.

### 2. Backend Server (`main.py`)
*   **Technology**: Python, FastAPI, Uvicorn.
*   **Role**: The central hub that connects the frontend to the AI agents.
*   **Key Components**:
    *   **`InMemoryRunner`**: A Google ADK component that manages the execution of agents. It handles the conversation state and tool execution.
    *   **Session Management**: Uses `InMemorySessionService` to maintain conversation context (history) for each user session.
    *   **`/ask` Endpoint**: The main entry point for user queries. It creates a session and runs the agent runner.

### 3. AI Agents (`agents/`)
Built using the **Google Agent Development Kit (ADK)** and **Gemini** models.

*   **Coordinator (`coordinator.py`)**:
    *   **Role**: The "Router". It doesn't do the work itself but delegates to the right specialist.
    *   **Logic**: "If the user wants to find a manual, call Search Agent. If they want to write one, call Manual Agent."

*   **Manual Agent (`manual_agent.py`)**:
    *   **Role**: The "Interviewer". It guides the user to provide all necessary details for a manual (Title, Steps, etc.).
    *   **Output**: A structured manual object (dictionary).

*   **Data Agent (`data_agent.py`)**:
    *   **Role**: The "Librarian". It takes the structured manual and saves it to the database.
    *   **Tools**: `save_manual_tool`.

*   **Search Agent (`search_agent.py`)**:
    *   **Role**: The "Researcher". It searches the database for existing manuals.
    *   **Tools**: `search_manuals_tool`, `get_manual_tool`.

*   **Generator Agent (`generator_agent.py`)**:
    *   **Role**: The "Writer". It takes an existing manual and repurposes it (e.g., "Make a checklist from this manual").

### 4. Storage Layer (`manual_store_gcp.py`)
*   **Technology**: Google BigQuery, Google Cloud Storage (GCS).
*   **Role**: Persists the manual data.
*   **BigQuery**: Stores metadata (ID, Title, Description, Keywords) for fast searching.
*   **Cloud Storage**: Stores the full content (HTML/Markdown) of the manual.

## 🛠️ Google ADK Patterns Used

*   **`LlmAgent`**: The base class for all agents. It defines the model (Gemini), instructions (System Prompt), and available tools.
*   **`InMemoryRunner`**: Executes the agent loop. It manages:
    *   **Event Loop**: Sending user messages and receiving agent events (thoughts, tool calls, responses).
    *   **Tool Execution**: Automatically calling Python functions when the model requests them.
*   **`InMemorySessionService`**: Stores the conversation history in memory (RAM). *Note: In a production app, you'd use a database-backed session service.*
