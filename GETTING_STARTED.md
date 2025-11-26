# 🎯 Getting Started Checklist

Follow these steps in order to get Manuel El Manual running locally:

## ✅ Phase 1: Environment Setup

- [ ] **Install Python 3.10+**
  ```bash
  python3 --version
  ```

- [ ] **Clone/Navigate to project**
  ```bash
  cd /Users/jigarkumarshah/AI_Projects/AI-project/Resume_builder/Hackathon
  ```

---

## ✅ Phase 2: Google Cloud Platform Setup

- [ ] **Create or select GCP project**
  - Go to: https://console.cloud.google.com/
  - Note your Project ID

- [ ] **Enable required APIs**
  ```bash
  gcloud services enable bigquery.googleapis.com
  gcloud services enable storage.googleapis.com
  gcloud services enable aiplatform.googleapis.com
  ```

- [ ] **Authenticate with GCP**
  ```bash
  gcloud auth application-default login
  ```

- [ ] **Create BigQuery dataset and tables**
  ```bash
  bq query < setup_bigquery.sql
  ```

- [ ] **Create Cloud Storage bucket**
  ```bash
  gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_BUCKET_NAME
  ```

---

## ✅ Phase 3: Google AI Setup

- [ ] **Get Gemini API key**
  - Go to: https://aistudio.google.com/app/apikey
  - Create and copy your API key

---

## ✅ Phase 4: Project Configuration

- [ ] **Run quick start script**
  ```bash
  ./quickstart.sh
  ```

- [ ] **Copy environment file**
  ```bash
  cp .env.example .env
  ```

- [ ] **Edit .env with your credentials**
  ```bash
  nano .env
  ```
  
  Fill in:
  - `GCP_PROJECT_ID` - Your GCP project ID
  - `MANUALS_BUCKET` - Your GCS bucket name
  - `GOOGLE_API_KEY` - Your Gemini API key

---

## ✅ Phase 5: Run the Application

- [ ] **Activate virtual environment**
  ```bash
  source venv/bin/activate
  ```

- [ ] **Start the server**
  ```bash
  python main.py
  ```

- [ ] **Open in browser**
  - Navigate to: http://127.0.0.1:8080

- [ ] **Test the application**
  - Click "📝 Crear manual"
  - Try creating a test manual
  - Test voice features

---

## 🎉 Success Criteria

You should see:
- ✅ Server running on port 8080
- ✅ All 5 agents initialized
- ✅ Web interface loads
- ✅ Can send messages to agents
- ✅ Manuals are saved to BigQuery

---

## 🆘 Troubleshooting

### Problem: Missing dependencies
**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: GCP authentication error
**Solution:**
```bash
gcloud auth application-default login
```

### Problem: BigQuery permission denied
**Solution:** Ensure your GCP account has BigQuery Admin role

### Problem: Port 8080 in use
**Solution:** Change port in `main.py` line 94:
```python
uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)
```

---

## 📚 Next Steps

After everything is working:

1. **Create your first manual**
   - Use natural language in Spanish
   - The AI will guide you through the process

2. **Explore features**
   - Voice input/output
   - Manual search
   - Summary generation
   - Checklist creation

3. **Customize**
   - Modify agent instructions
   - Add new agents
   - Customize the UI

---

## 📖 Documentation

- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup guide
- [setup_bigquery.sql](setup_bigquery.sql) - Database schema

---

**Questions?** Check SETUP_GUIDE.md troubleshooting section or the Google ADK documentation.
