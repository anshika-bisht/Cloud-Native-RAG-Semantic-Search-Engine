from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.repositories.document import DocumentRepository
from app.repositories.session import SessionRepository
from app.repositories.query_log import QueryLogRepository

from app.services.llm.base import LLMProvider
from app.services.vectorstore.base import VectorStore
from app.services.embeddings.service import EmbeddingService
from app.services.parser.service import DocumentParser
from app.services.chunking.service import SemanticSlidingWindowChunker
from app.services.retrieval.service import RAGOrchestrator

# Global Singletons for ML Models & Cloud Clients
_embedding_service = EmbeddingService()
_parser_service = DocumentParser()
_chunking_service = SemanticSlidingWindowChunker()

# Strategy Resolution: Vector Store
if settings.VECTOR_STORE_PROVIDER.lower() == "qdrant":
    from app.services.vectorstore.qdrant import QdrantVectorStore
    _vector_store: VectorStore = QdrantVectorStore(dimension=_embedding_service.dimension)
else:
    from app.services.vectorstore.faiss import FAISSVectorStore
    _vector_store: VectorStore = FAISSVectorStore(dimension=_embedding_service.dimension)

# Strategy Resolution: LLM Provider
if settings.LLM_PROVIDER.lower() == "gemini":
    from app.services.llm.gemini import GeminiProvider
    _llm_provider: LLMProvider = GeminiProvider()
elif settings.LLM_PROVIDER.lower() == "ollama":
    from app.services.llm.ollama import OllamaProvider
    _llm_provider: LLMProvider = OllamaProvider()
else:
    from app.services.llm.groq import GroqProvider
    _llm_provider: LLMProvider = GroqProvider()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_document_repo(session: AsyncSession = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(session)

def get_session_repo(session: AsyncSession = Depends(get_db_session)) -> SessionRepository:
    return SessionRepository(session)

def get_query_log_repo(session: AsyncSession = Depends(get_db_session)) -> QueryLogRepository:
    return QueryLogRepository(session)

def get_vector_store() -> VectorStore:
    return _vector_store

def get_llm_provider() -> LLMProvider:
    return _llm_provider

def get_embedding_service() -> EmbeddingService:
    return _embedding_service

def get_parser() -> DocumentParser:
    return _parser_service

def get_chunker() -> SemanticSlidingWindowChunker:
    return _chunking_service

def get_rag_orchestrator(
    llm: LLMProvider = Depends(get_llm_provider),
    vector_store: VectorStore = Depends(get_vector_store),
    embeddings: EmbeddingService = Depends(get_embedding_service),
    doc_repo: DocumentRepository = Depends(get_document_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
    log_repo: QueryLogRepository = Depends(get_query_log_repo)
) -> RAGOrchestrator:
    return RAGOrchestrator(llm, vector_store, embeddings, doc_repo, session_repo, log_repo)
