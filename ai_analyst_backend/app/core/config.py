import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    PROJECT_ID: str = "ai-analyst-agent-472807"
    LOCATION: str = "us-central1"
    BUCKET_NAME: str = "ai-analysis-agent-data"
    BIGQUERY_DATASET: str = "startup_benchmarks"
    # --- NEW: Gemini API Key for Google AI Studio ---
    GEMINI_API_KEY: str = "AIzaSyCMdNKoVgc6uRlJRWtu0sfHTaSqjL0ra3s"

settings = Settings()
