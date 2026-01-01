from typing import Optional
from .engine_base import BaseLLMEngine
import logging

try:
    import google.generativeai as genai  
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

logger = logging.getLogger(__name__)

class GeminiEngine(BaseLLMEngine):
    """
    Wrapper for google.generativeai client.
    Configures once in __init__ and reuses the model object.
    If the package isn't available, raises a helpful error when generate() is called.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self._client_configured = False
        self._model = None
        if HAS_GENAI and api_key:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(self.model_name)
                self._client_configured = True
            except Exception as e:
                logger.exception("Failed to configure Gemini client: %s", e)
                self._client_configured = False

    def generate(self, prompt: str, *, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        if not HAS_GENAI:
            raise RuntimeError("google.generativeai library not installed. Install it or use a different engine.")
        if not self._client_configured or self._model is None:
            raise RuntimeError("Gemini engine not configured correctly (check API key and package).")

        kwargs = {}
        if max_tokens:
            kwargs["max_output_tokens"] = max_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature

        try:
            response = self._model.generate_content(prompt, **kwargs)
            if hasattr(response, "text"):
                return response.text or ""
            elif isinstance(response, dict) and response.get("content"):
                return response.get("content", "")
            else:
                return str(response)
        except Exception as e:
            logger.exception("Gemini generate failed: %s", e)
            raise
