import os
from dataclasses import dataclass

@dataclass
class Settings:
    """
    Simple settings loader. Prefer environment variables for secrets.
    """
    api_key: str = os.environ.get("JARVIS_API_KEY", "")
    gemini_model_name: str = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    ollama_url: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    history_file: str = os.environ.get("JARVIS_HISTORY_FILE", "History.json")

