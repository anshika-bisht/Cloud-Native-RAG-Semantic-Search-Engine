import os
import asyncio
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple

from app.services.vectorstore.base import VectorStore
from app.core.config import settings
from app.core.logger import logger

class FAISSVectorStore(VectorStore):
    """
    Fallback local vector store using FAISS.
    Useful for local development without Docker.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index_path = settings.FAISS_INDEX_PATH
        self.index = None
        
        # FAISS does not store payloads natively. We map faiss_id (int) -> chunk_id (str)
        # and faiss_id -> document_id (str) in memory for this fallback implementation.
        self.id_to_chunk = {}
        self.chunk_to_id = {}
        self.id_to_document = {}
        self._next_id = 0

    async def create_collection(self) -> None:
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            # In a real FAISS system with persistence, we'd need to load the ID mapping too.
            # For this fallback, we just re-init memory mappings.
            self._next_id = self.index.ntotal
        else:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            logger.info("Created new FAISS index.")

    async def add_embeddings(self, ids: List[str], embeddings: List[List[float]], payloads: List[Dict[str, Any]] = None) -> None:
        if not embeddings:
            return
            
        vectors = np.array(embeddings).astype('float32')
        faiss.normalize_L2(vectors)
        
        self.index.add(vectors)
        
        for i, chunk_id in enumerate(ids):
            faiss_id = self._next_id + i
            self.id_to_chunk[faiss_id] = chunk_id
            self.chunk_to_id[chunk_id] = faiss_id
            if payloads and "document_id" in payloads[i]:
                self.id_to_document[faiss_id] = payloads[i]["document_id"]
                
        self._next_id += len(ids)
        await self._save_index()

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        if self.index.ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(vector)
        
        distances, indices = self.index.search(vector, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx in self.id_to_chunk:
                results.append((self.id_to_chunk[idx], float(dist)))
        return results

    async def delete_by_document(self, document_id: str) -> None:
        # FAISS IndexFlat does not support dynamic deletion easily.
        # In a real FAISS system, we use IndexIDMap. 
        # Since this is a fallback, we log a warning.
        logger.warning(f"Deletion by document_id ({document_id}) is not natively supported in this FAISS fallback. Use Qdrant for full CRUD.")

    async def health_check(self) -> bool:
        return self.index is not None

    async def _save_index(self):
        # Run in a thread to prevent blocking
        await asyncio.to_thread(faiss.write_index, self.index, self.index_path)
