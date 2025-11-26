# 🚀 Manuel El Manual - Local Setup Guide

## Prerequisites

Before running this project, ensure you have:

1. **Python 3.10+** installed
2. **Google Cloud Platform (GCP) Account** with:
   - BigQuery API enabled
   - Cloud Storage API enabled
   - Service account with appropriate permissions
3. **Google AI API Key** (for Gemini models)

---

## Step 1: Clone and Navigate to Project

```bash
cd /Users/jigarkumarshah/AI_Projects/AI-project/Resume_builder/Hackathon
```

---

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: The `requirements.txt` includes `pywin32` which is Windows-specific. On macOS, pip will skip it automatically.

---

## Step 4: Missing Files to Create

The project is missing several critical files. You need to create:

### 4.1 Create `settings.py`

This file should contain your GCP configuration:

```python
# settings.py
import os
from pathlib import Path

# Google Cloud Project Configuration
PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
BQ_DATASET = "manuals_dataset"      # BigQuery dataset name
MANUALS_BUCKET = "your-bucket-name" # Cloud Storage bucket name

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-api-key-here")

# Optional: Path to GCP service account key (if not using default credentials)
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", None)
```

### 4.2 Create `.env` file (Optional but recommended)

Store sensitive credentials here:

```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
GCP_CREDENTIALS_PATH=/path/to/service-account-key.json
```

### 4.3 Create the main server file `main.py` or `app.py`

The project is missing the FastAPI server entry point. Create `main.py`:

```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.genai import types
import uvicorn

from agents.coordinator import create_coordinator
from agents.manual_agent import create_manual_agent
from agents.data_agent import create_data_agent
from agents.search_agent import create_search_agent
from agents.generator_agent import create_generator_agent
from manual_store_gcp import search_manuals

app = FastAPI(title="Manuel El Manual")

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

# Initialize agents
manual_agent = create_manual_agent(retry)
data_agent = create_data_agent(retry)
search_agent = create_search_agent(retry)
generator_agent = create_generator_agent(retry)
coordinator = create_coordinator(
    manual_agent, data_agent, search_agent, generator_agent, retry
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    return FileResponse("index.html")


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Process user questions through the coordinator agent"""
    try:
        response = coordinator.chat(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manuals")
async def get_manuals():
    """Get all manuals from BigQuery"""
    try:
        results = search_manuals("")  # Empty query returns all manuals
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True
    )
```

---

## Step 5: Set Up Google Cloud Platform

### 5.1 Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 5.2 Enable Required APIs

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 5.3 Create BigQuery Dataset and Tables

Run this SQL in BigQuery console:

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS manuals_dataset;

-- Create manuals_dict table
CREATE TABLE IF NOT EXISTS manuals_dataset.manuals_dict (
  manual_id STRING NOT NULL,
  title STRING,
  business_area STRING,
  requester STRING,
  created_by STRING,
  created_at TIMESTAMP,
  last_updated TIMESTAMP,
  context STRING,
  requirements STRING,
  permissions STRING,
  outputs STRING,
  keywords ARRAY<STRING>
);

-- Create manual_steps table
CREATE TABLE IF NOT EXISTS manuals_dataset.manual_steps (
  manual_id STRING NOT NULL,
  step_number INT64,
  step_title STRING,
  step_description STRING,
  expected_output STRING,
  required_tools STRING,
  estimated_time STRING,
  is_critical BOOL
);

-- Create manual_files table
CREATE TABLE IF NOT EXISTS manuals_dataset.manual_files (
  manual_id STRING NOT NULL,
  version INT64,
  file_path STRING,
  format STRING,
  created_at TIMESTAMP,
  created_by STRING
);
```

### 5.4 Create Cloud Storage Bucket

```bash
gsutil mb -p your-project-id -l us-central1 gs://your-bucket-name
```

### 5.5 Set Up Authentication

**Option A: Application Default Credentials (Recommended for local development)**

```bash
gcloud auth application-default login
```

**Option B: Service Account Key**

1. Create a service account in GCP Console
2. Grant roles: BigQuery Admin, Storage Admin, Vertex AI User
3. Download JSON key file
4. Set environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

---

## Step 6: Get Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create an API key
3. Add it to your `.env` file or `settings.py`

---

## Step 7: Run the Application

### Start the Backend Server

```bash
# Make sure virtual environment is activated
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

### Access the Application

1. Open your browser
2. Navigate to: `http://127.0.0.1:8080`
3. You should see the "Manuel El Manual" interface

---

## Step 8: Test the Application

1. Click "📝 Crear manual" or type in chat: "Quiero crear un manual nuevo"
2. Follow the prompts from the AI agent
3. Test voice features by clicking the microphone button (requires browser permissions)

---

## Troubleshooting

### Issue: `ImportError: cannot import name 'settings'`

**Solution**: Make sure you created `settings.py` with the correct GCP configuration.

### Issue: `google.auth.exceptions.DefaultCredentialsError`

**Solution**: Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`.

### Issue: `Permission denied` errors in BigQuery

**Solution**: Ensure your GCP account/service account has BigQuery Admin role.

### Issue: Port 8080 already in use

**Solution**: Change the port in `main.py`:
```python
uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)
```

And update `index.html` line 188:
```javascript
const API_BASE = "http://127.0.0.1:8081";
```

---

## Project Structure

```
Hackathon/
├── agents/
│   ├── coordinator.py      # Main coordinator agent
│   ├── manual_agent.py     # Manual creation agent
│   ├── data_agent.py       # Data persistence agent
│   ├── search_agent.py     # Search agent
│   └── generator_agent.py  # Content generation agent
├── index.html              # Frontend UI
├── main.py                 # FastAPI server (YOU NEED TO CREATE THIS)
├── manual_store_gcp.py     # GCP storage interface
├── settings.py             # Configuration (YOU NEED TO CREATE THIS)
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (OPTIONAL)
```

---

## Next Steps

1. ✅ Set up GCP project and authentication
2. ✅ Create missing files (`settings.py`, `main.py`)
3. ✅ Install dependencies
4. ✅ Run the server
5. 🎉 Start creating manuals!

---

## Additional Resources

- [Google ADK Documentation](https://github.com/google/adk)
- [BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
