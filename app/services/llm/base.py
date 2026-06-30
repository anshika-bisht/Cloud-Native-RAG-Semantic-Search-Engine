from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generates a text response for the given prompt."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Returns the identifier of the active model."""
        pass
