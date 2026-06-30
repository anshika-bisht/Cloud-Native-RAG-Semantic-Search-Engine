import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.logger import logger

class EmbeddingService:
    """
    Generates high-quality vector embeddings.
    Implements a simple in-memory cache to prevent re-embedding identical chunks.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self._cache = {}
        logger.info(f"Loaded EmbeddingService with {model_name} (dim: {self.dimension})")

    async def embed_text(self, text: str) -> List[float]:
        if text in self._cache:
            return self._cache[text]
        
        # Offload to thread to prevent event loop blocking
        embedding = await asyncio.to_thread(self.model.encode, text)
        result = embedding.tolist()
        
        self._cache[text] = result
        return result

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Fast path if all exist in cache
        if all(t in self._cache for t in texts):
            return [self._cache[t] for t in texts]

        # Process uncached in batch for performance
        uncached = [t for t in texts if t not in self._cache]
        if uncached:
            embeddings_matrix = await asyncio.to_thread(
                self.model.encode, 
                uncached, 
                batch_size=32,
                show_progress_bar=False
            )
            for i, text in enumerate(uncached):
                self._cache[text] = embeddings_matrix[i].tolist()
                
        return [self._cache[t] for t in texts]
