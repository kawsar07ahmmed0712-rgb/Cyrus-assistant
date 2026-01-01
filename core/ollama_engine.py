from typing import Optional
from .engine_base import BaseLLMEngine
import requests
import logging

logger = logging.getLogger(__name__)

class OllamaEngine(BaseLLMEngine):
    """
    Minimal Ollama HTTP wrapper.
    Expects Ollama running at provided base_url.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:4b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, *, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model,
            "prompt": prompt,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and "choices" in data and data["choices"]:
                choice = data["choices"][0]
                for key in ("text", "content", "message"):
                    if isinstance(choice, dict) and key in choice:
                        return choice[key]
                return str(choice)
            return str(data)
        except Exception as e:
            logger.exception("Ollama generate failed: %s", e)
            raise

