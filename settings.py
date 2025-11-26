# settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Cloud Project Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
BQ_DATASET = os.getenv("BQ_DATASET", "manuals_dataset")
MANUALS_BUCKET = os.getenv("MANUALS_BUCKET", "your-bucket-name")

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Optional: Path to GCP service account key
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", None)

# Set credentials if path is provided
if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CREDENTIALS_PATH
