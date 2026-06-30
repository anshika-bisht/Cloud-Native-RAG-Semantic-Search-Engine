import time
import asyncio
from typing import Tuple, List

from app.services.llm.base import LLMProvider
from app.services.vectorstore.base import VectorStore
from app.services.embeddings.service import EmbeddingService
from app.repositories.document import DocumentRepository
from app.repositories.session import SessionRepository
from app.repositories.query_log import QueryLogRepository
from app.models.orm import QueryLog
from app.core.prompts import RAG_STRICT_TEMPLATE
from app.core.logger import logger

class RAGOrchestrator:
    """
    Coordinates Retrieval-Augmented Generation workflows.
    Decoupled from specific LLMs or Vector DBs via interfaces.
    """
    def __init__(
        self,
        llm: LLMProvider,
        vector_store: VectorStore,
        embeddings: EmbeddingService,
        doc_repo: DocumentRepository,
        session_repo: SessionRepository,
        log_repo: QueryLogRepository
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.doc_repo = doc_repo
        self.session_repo = session_repo
        self.log_repo = log_repo

    async def process_query(self, query: str, session_id: str = None, top_k: int = 5) -> Tuple[str, List[str], dict]:
        metrics = {}
        
        # 1. Embed Query
        start = time.time()
        query_embedding = await self.embeddings.embed_text(query)
        metrics["embedding_latency_ms"] = (time.time() - start) * 1000
        
        # 2. Retrieve Vectors
        start = time.time()
        hits = await self.vector_store.search(query_embedding, top_k)
        metrics["retrieval_latency_ms"] = (time.time() - start) * 1000
        
        chunk_ids = [hit[0] for hit in hits]
        
        # 3. Fetch Source Text
        chunks = await self.doc_repo.get_chunks_by_ids(chunk_ids)
        context_text = "\n\n".join([f"- {c.text}" for c in chunks])
        
        # 4. Fetch History
        history_text = ""
        if session_id:
            session = await self.session_repo.get_with_history(session_id)
            if session:
                history_text = "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in session.history[-5:]])
        
        # 5. Build Prompt & Generate
        prompt = RAG_STRICT_TEMPLATE.format(
            context=context_text if context_text else "No relevant context found.",
            history=history_text,
            query=query
        )
        
        start = time.time()
        answer = await self.llm.generate(prompt)
        metrics["inference_latency_ms"] = (time.time() - start) * 1000
        metrics["total_latency_ms"] = metrics["embedding_latency_ms"] + metrics["retrieval_latency_ms"] + metrics["inference_latency_ms"]
        
        # 6. Save History & Log Metrics
        if session_id:
            await self.session_repo.add_message(session_id, "user", query)
            await self.session_repo.add_message(session_id, "assistant", answer)
            
        await self.log_repo.add(QueryLog(
            session_id=session_id,
            query_text=query,
            llm_response=answer,
            embedding_latency_ms=metrics["embedding_latency_ms"],
            retrieval_latency_ms=metrics["retrieval_latency_ms"],
            inference_latency_ms=metrics["inference_latency_ms"],
            total_latency_ms=metrics["total_latency_ms"]
        ))
        
        return answer, [c.text for c in chunks], metrics
