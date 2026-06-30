from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.dependencies import get_db_session, get_vector_store, get_llm_provider
from app.schemas.domain import StatResponse
from app.models.orm import Document, Chunk, QueryLog
from app.services.vectorstore.base import VectorStore
from app.services.llm.base import LLMProvider

router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check(
    vector_store: VectorStore = Depends(get_vector_store),
    llm: LLMProvider = Depends(get_llm_provider)
):
    vs_healthy = await vector_store.health_check()
    return {
        "status": "ok" if vs_healthy else "degraded",
        "vector_store": "online" if vs_healthy else "offline",
        "llm_provider": llm.get_model_name()
    }

@router.get("/stats", response_model=StatResponse)
async def get_stats(session = Depends(get_db_session)):
    doc_count = await session.execute(select(func.count()).select_from(Document))
    chunk_count = await session.execute(select(func.count()).select_from(Chunk))
    query_count = await session.execute(select(func.count()).select_from(QueryLog))
    
    return StatResponse(
        total_documents=doc_count.scalar() or 0,
        total_chunks=chunk_count.scalar() or 0,
        total_queries=query_count.scalar() or 0
    )

@router.get("/metrics")
async def get_metrics(session = Depends(get_db_session)):
    # Calculate average latencies
    avg_total = await session.execute(select(func.avg(QueryLog.total_latency_ms)))
    avg_retrieval = await session.execute(select(func.avg(QueryLog.retrieval_latency_ms)))
    avg_inference = await session.execute(select(func.avg(QueryLog.inference_latency_ms)))
    
    return {
        "average_total_latency_ms": round(avg_total.scalar() or 0, 2),
        "average_retrieval_latency_ms": round(avg_retrieval.scalar() or 0, 2),
        "average_inference_latency_ms": round(avg_inference.scalar() or 0, 2)
    }
