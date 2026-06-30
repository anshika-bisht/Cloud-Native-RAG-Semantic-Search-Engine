from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Schemas
class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question.")
    session_id: Optional[str] = Field(default=None, description="Session ID for maintaining conversation history.")
    top_k: int = Field(default=5, description="Number of document chunks to retrieve.")

# Response Schemas
class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime
    
class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    message: str

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    context_retrieved: List[str]
    retrieval_latency_ms: float
    inference_latency_ms: float
    total_latency_ms: float

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: datetime

class SessionResponse(BaseModel):
    session_id: str
    title: str
    history: List[ChatMessage]

class StatResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
