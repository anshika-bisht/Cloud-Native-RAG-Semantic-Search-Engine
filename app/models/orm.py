import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    content_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")  # pending, processing, indexed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    
    document = relationship("Document", back_populates="chunks")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    history = relationship("ConversationHistory", back_populates="session", cascade="all, delete-orphan")

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    session = relationship("Session", back_populates="history")

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    
    embedding_latency_ms = Column(Float, nullable=False, default=0.0)
    retrieval_latency_ms = Column(Float, nullable=False, default=0.0)
    inference_latency_ms = Column(Float, nullable=False, default=0.0)
    total_latency_ms = Column(Float, nullable=False, default=0.0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
