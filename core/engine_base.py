
from abc import ABC, abstractmethod
from typing import Optional

class BaseLLMEngine(ABC):
    """
    Abstract LLM engine interface used by JarvisAssistant.
    Implementations should be safe and idempotent.
    """

    @abstractmethod
    def generate(self, prompt: str, *, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """
        Generate a text response for the given prompt.
        Should return a plain string (not an object).
        """
        raise NotImplementedError
