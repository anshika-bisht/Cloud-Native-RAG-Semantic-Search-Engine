from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class VectorStore(ABC):
    """
    Abstract Interface for Vector Database operations.
    Allows seamlessly swapping implementations (e.g., Qdrant, FAISS, Pinecone).
    """

    @abstractmethod
    async def create_collection(self) -> None:
        """Initializes the collection/index if it does not exist."""
        pass

    @abstractmethod
    async def add_embeddings(self, ids: List[str], embeddings: List[List[float]], payloads: List[Dict[str, Any]] = None) -> None:
        """Upserts a batch of vectors and their corresponding metadata payloads."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Searches for the closest vectors. Returns list of (chunk_id, distance_score)."""
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: str) -> None:
        """Deletes all vectors associated with a specific document_id."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if the vector store is online and accessible."""
        pass
