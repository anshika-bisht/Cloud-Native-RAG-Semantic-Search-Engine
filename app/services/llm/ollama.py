import ollama
import asyncio
from app.services.llm.base import LLMProvider
from app.core.config import settings
from app.core.logger import logger

class OllamaProvider(LLMProvider):
    """
    Fallback LLM Provider for local development using Ollama.
    """
    def __init__(self):
        self.model = settings.OLLAMA_MODEL_NAME
        # Use an AsyncClient pointing to the configured host
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        logger.info(f"Initialized OllamaProvider with model: {self.model}")

    async def generate(self, prompt: str) -> str:
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.0}
        )
        return response['response']

    def get_model_name(self) -> str:
        return f"ollama:{self.model}"
