import google.generativeai as genai
from app.services.llm.base import LLMProvider
from app.core.config import settings
from app.core.logger import logger
import asyncio

class GeminiProvider(LLMProvider):
    """
    Alternative LLM Provider using Google Gemini.
    """
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL_NAME
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized GeminiProvider with model: {self.model_name}")

    async def generate(self, prompt: str) -> str:
        # Offload to thread since google-generativeai may block
        response = await asyncio.to_thread(
            self.model.generate_content, 
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        return response.text

    def get_model_name(self) -> str:
        return f"gemini:{self.model_name}"
