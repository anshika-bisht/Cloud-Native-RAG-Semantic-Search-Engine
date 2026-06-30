from fastapi import APIRouter, Depends
from app.api.dependencies import get_rag_orchestrator
from app.schemas.domain import QueryRequest, QueryResponse
from app.services.retrieval.service import RAGOrchestrator

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator)
):
    answer, context, metrics = await orchestrator.process_query(
        query=request.query,
        session_id=request.session_id,
        top_k=request.top_k
    )
    
    return QueryResponse(
        answer=answer,
        session_id=request.session_id or "anonymous",
        context_retrieved=context,
        retrieval_latency_ms=metrics.get("retrieval_latency_ms", 0),
        inference_latency_ms=metrics.get("inference_latency_ms", 0),
        total_latency_ms=metrics.get("total_latency_ms", 0)
    )
