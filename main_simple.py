# main_simple.py - Simplified FastAPI Server WITHOUT Runner
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
import uvicorn
import os

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

# Simple model client without complex agents
client = genai.Client()

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
    Process user questions using simple Gemini API call.
    """
    try:
        print(f"\n💬 User question: {request.question}")
        
        # Direct Gemini API call
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=request.question
        )
        
        answer = response.text
        
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
        "model": "gemini-2.0-flash-exp"
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 Starting Manuel El Manual Server (Simplified)")
    print("="*60)
    print("📍 URL: http://127.0.0.1:8080")
    print("📖 Docs: http://127.0.0.1:8080/docs")
    print("💡 Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main_simple:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )
