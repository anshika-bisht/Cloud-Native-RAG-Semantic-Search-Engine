import asyncio
from groq import AsyncGroq
from app.services.llm.base import LLMProvider
from app.core.config import settings
from app.core.logger import logger

class GroqProvider(LLMProvider):
    """
    Primary LLM Provider utilizing Groq's high-speed inference API.
    """
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL_NAME
        logger.info(f"Initialized GroqProvider with model: {self.model}")

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.0,  # Zero for strict RAG
            max_tokens=1024
        )
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"groq:{self.model}"
