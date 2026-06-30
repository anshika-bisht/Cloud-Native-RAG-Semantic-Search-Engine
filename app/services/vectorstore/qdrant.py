import uuid
from typing import List, Dict, Any, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.services.vectorstore.base import VectorStore
from app.core.config import settings
from app.core.logger import logger

class QdrantVectorStore(VectorStore):
    """
    Production-grade Vector Store utilizing Qdrant Cloud or Local Docker.
    """
    def __init__(self, dimension: int = 384):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dimension = dimension
        
        # Initialize Async Qdrant Client
        if settings.QDRANT_API_KEY:
            # Qdrant Cloud
            self.client = AsyncQdrantClient(
                url=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            # Local Docker Qdrant
            self.client = AsyncQdrantClient(
                host=settings.QDRANT_HOST, 
                port=settings.QDRANT_PORT
            )

    async def create_collection(self) -> None:
        if not await self.client.collection_exists(self.collection_name):
            logger.info(f"Creating Qdrant collection '{self.collection_name}'")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )
            # Create an index on document_id for fast deletion
            await self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_id",
                field_schema="keyword"
            )

    async def add_embeddings(self, ids: List[str], embeddings: List[List[float]], payloads: List[Dict[str, Any]] = None) -> None:
        points = []
        for i, (chunk_id, embedding) in enumerate(zip(ids, embeddings)):
            payload = payloads[i] if payloads else {}
            # Qdrant requires UUID or integer IDs
            qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            payload["_original_chunk_id"] = chunk_id
            
            points.append(
                PointStruct(id=qdrant_id, vector=embedding, payload=payload)
            )
            
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        hits = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        # Map Qdrant hits back to our original chunk_ids
        return [(hit.payload["_original_chunk_id"], hit.score) for hit in hits if "_original_chunk_id" in hit.payload]

    async def delete_by_document(self, document_id: str) -> None:
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        )

    async def health_check(self) -> bool:
        try:
            collections = await self.client.get_collections()
            return collections is not None
        except Exception:
            return False
