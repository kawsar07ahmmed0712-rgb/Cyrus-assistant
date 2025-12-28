import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()
        self.api_key = self._load_api_key()

    @staticmethod
    def _load_api_key() -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not found. Please set it in your .env file."
            )
        return api_key

