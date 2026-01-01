from typing import Optional
from .engine_base import BaseLLMEngine
import logging

logger = logging.getLogger(__name__)

class JarvisAssistant:
    """
    Thin orchestrator that talks to an LLM engine. Keeps interface small and testable.
    """

    def __init__(self, engine: BaseLLMEngine, prompt_controller = None, memory = None):
        self.prompt_controller = prompt_controller
        self.engine = engine
        self.memory = memory

    def respond(self, prompt: str, *, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """
        Call engine.generate and handle exceptions cleanly.
        """
        try:
            response = self.engine.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            return response or ""
        except Exception as e:
            logger.exception("LLM engine call failed: %s", e)
            return f"Model call failed: {e}"
