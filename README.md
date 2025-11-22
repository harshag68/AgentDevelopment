# 📚 Manuel El Manual

> AI-powered system for creating and managing internal company manuals

Manuel El Manual is a multi-agent AI system that helps teams create comprehensive, structured documentation through natural conversation. Built with Google's Agent Development Kit (ADK) and powered by Gemini AI.

---

## ✨ Features

- 🤖 **Multi-Agent Architecture**: 5 specialized AI agents working together
- 🗣️ **Voice-Enabled**: Speak or type in Spanish
- 💾 **Cloud Storage**: Automatic persistence to Google Cloud Platform
- 🔍 **Smart Search**: Find existing manuals to avoid duplication
- 📝 **Guided Creation**: AI asks the right questions to build complete manuals
- 🎯 **Multiple Outputs**: Generate summaries, checklists, and communication materials

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Platform account
- Google AI API key

### Installation

1. **Run the quick start script:**
   ```bash
   ./quickstart.sh
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   nano .env
   ```

3. **Set up BigQuery tables:**
   ```bash
   bq query < setup_bigquery.sql
   ```

4. **Create GCS bucket:**
   ```bash
   gsutil mb -p YOUR_PROJECT_ID gs://YOUR_BUCKET_NAME
   ```

5. **Start the server:**
   ```bash
   python main.py
   ```

6. **Open your browser:**
   ```
   http://127.0.0.1:8080
   ```

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 🏗️ Architecture

### AI Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Manuel** (Coordinator) | Orchestrates all agents | Routes requests to specialists |
| **Italo** (Manual Agent) | Creates manuals | Structured documentation, step-by-step procedures |
| **Lorena** (Data Agent) | Manages persistence | Saves to BigQuery & Cloud Storage |
| **Sofia** (Search Agent) | Finds manuals | Text search, retrieval |
| **Emilio** (Generator Agent) | Creates summaries | Checklists, executive summaries |

### Tech Stack

- **Backend**: Python, FastAPI, Google ADK
- **AI**: Gemini 2.5 Flash
- **Database**: Google BigQuery
- **Storage**: Google Cloud Storage
- **Frontend**: Vanilla HTML/CSS/JavaScript

---

## 📖 Usage Examples

### Create a Manual
```
User: "Quiero crear un manual para onboarding de analistas de datos"
Manuel: "¡Perfecto! Vamos a crear ese manual. Cuéntame..."
```

### Search Manuals
Click "🔍 Buscar manual" or:
```
User: "Busca manuales sobre Python"
```

### Generate Summary
```
User: "Dame un resumen ejecutivo del manual MAN-abc123"
```

---

## 🗂️ Project Structure

```
Hackathon/
├── agents/                 # AI agent implementations
│   ├── coordinator.py     # Main coordinator
│   ├── manual_agent.py    # Manual creation
│   ├── data_agent.py      # Data persistence
│   ├── search_agent.py    # Search functionality
│   └── generator_agent.py # Content generation
├── main.py                # FastAPI server
├── settings.py            # Configuration
├── manual_store_gcp.py    # GCP storage interface
├── index.html             # Frontend UI
├── requirements.txt       # Dependencies
├── setup_bigquery.sql     # Database schema
├── quickstart.sh          # Quick setup script
└── .env.example           # Environment template
```

---

## ⚙️ Configuration

Edit `.env` with your settings:

```bash
GCP_PROJECT_ID=your-project-id
BQ_DATASET=manuals_dataset
MANUALS_BUCKET=your-bucket-name
GOOGLE_API_KEY=your-api-key
```

---

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve web interface |
| `/ask` | POST | Process questions |
| `/manuals` | GET | List all manuals |
| `/health` | GET | Health check |

---

## 🤝 Contributing

This is a hackathon project. Feel free to extend it with:
- Additional agents (translation, approval workflows)
- More output formats (PDF, Word)
- Integration with other systems
- Enhanced search capabilities

---

## 📄 License

MIT License - feel free to use and modify

---

## 🆘 Support

For issues or questions, see [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section.

---

**Built with ❤️ using Google ADK and Gemini AI**
