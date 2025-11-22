# main.py - FastAPI Server for Manuel El Manual
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.genai import types
from google.adk.runners import InMemoryRunner
import uvicorn
import os
import asyncio

from agents.coordinator import create_coordinator
from agents.manual_agent import create_manual_agent
from agents.data_agent import create_data_agent
from agents.search_agent import create_search_agent
from agents.generator_agent import create_generator_agent
from manual_store_gcp import search_manuals

app = FastAPI(
    title="Manuel El Manual",
    description="AI-powered manual creation and management system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retry options for agents
retry = types.HttpRetryOptions()

print("🚀 Initializing AI agents...")

# Initialize agents
try:
    manual_agent = create_manual_agent(retry)
    print("✅ Manual Agent (Italo) initialized")
    
    data_agent = create_data_agent(retry)
    print("✅ Data Agent (Lorena) initialized")
    
    search_agent = create_search_agent(retry)
    print("✅ Search Agent (Sofia) initialized")
    
    generator_agent = create_generator_agent(retry)
    print("✅ Generator Agent (Emilio) initialized")
    
    coordinator = create_coordinator(
        manual_agent, data_agent, search_agent, generator_agent, retry
    )
    print("✅ Coordinator Agent (Manuel) initialized")
    
    # Initialize runner with app_name matching the package directory
    # The Runner is the engine that executes the agent.
    # We use InMemoryRunner for development, which stores session state in RAM.
    # 'app_name' is used to namespace the sessions.
    runner = InMemoryRunner(agent=coordinator, app_name="agents")
    print("✅ Runner initialized")
    print("🎉 All agents ready!\n")
except Exception as e:
    print(f"❌ Error initializing agents: {e}")
    raise


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    if not os.path.exists("index.html"):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse("index.html")


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Process user questions through the coordinator agent.
    
    The coordinator will route the question to the appropriate specialized agent:
    - Manual Agent (Italo): For creating/editing manuals
    - Data Agent (Lorena): For saving to GCP
    - Search Agent (Sofia): For finding existing manuals
    - Generator Agent (Emilio): For summaries and checklists
    """
    try:
        print(f"\n💬 User question: {request.question}")
        
        # Create a proper Content object for the message
        # The ADK expects a 'types.Content' object, not a raw string.
        message = types.Content(
            role="user",
            parts=[types.Part(text=request.question)]
        )
        
        # Generate a unique session ID for each request
        # In a real app, this would come from the client (e.g., cookie or header)
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create session explicitly before running
        # This fixes the "Session not found" error.
        # The Runner needs a session to exist in the SessionService before it can attach to it.
        await runner.session_service.create_session(
            app_name="agents",
            user_id="default_user",
            session_id=session_id
        )

        # Run the agent in a separate thread to avoid blocking the event loop
        # Note: runner.run is synchronous, so we use to_thread
        # BUT we need to consume the generator, so we define a helper
        def run_agent():
            final_response = ""
            # The runner.run method returns a generator of events.
            # We must iterate through ALL events to let the agent complete its work.
            # Events can be:
            # - Thought updates (agent thinking)
            # - Tool calls (agent asking to run a function)
            # - Final response (the text to show the user)
            for event in runner.run(
                user_id="default_user",
                session_id=session_id,
                new_message=message
            ):
                # The final event typically contains the response
                if hasattr(event, 'text'):
                    final_response = event.text
                elif hasattr(event, 'content'):
                    final_response = str(event.content)
                elif hasattr(event, 'message'):
                    final_response = str(event.message)
            return final_response
        
        # Execute the agent logic in a thread pool to keep the server responsive
        answer = await asyncio.to_thread(run_agent)
        
        # Fallback if no response found
        if not answer:
            answer = "No response generated"
        
        print(f"🤖 Agent response: {answer}\n")
        
        return {"answer": answer}
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/manuals")
async def get_manuals():
    """
    Get all manuals from BigQuery.
    Returns a list of manual metadata (without full step details).
    """
    try:
        print("\n📚 Fetching all manuals...")
        
        # Empty query returns all manuals sorted by last_updated DESC
        results = search_manuals("")
        
        print(f"✅ Found {len(results)} manuals\n")
        
        return {"results": results}
        
    except Exception as e:
        print(f"❌ Error fetching manuals: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching manuals: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents": {
            "coordinator": "Manuel",
            "manual_agent": "Italo",
            "data_agent": "Lorena",
            "search_agent": "Sofia",
            "generator_agent": "Emilio"
        }
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 Starting Manuel El Manual Server")
    print("="*60)
    print("📍 URL: http://127.0.0.1:8080")
    print("📖 Docs: http://127.0.0.1:8080/docs")
    print("💡 Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )
