from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from app.api.dependencies import get_session_repo
from app.schemas.domain import SessionResponse, ChatMessage
from app.repositories.session import SessionRepository
from app.models.orm import Session

router = APIRouter(tags=["Sessions"])

class CreateSessionRequest(BaseModel):
    title: str = "New Conversation"

@router.post("/session", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    repo: SessionRepository = Depends(get_session_repo)
):
    session = Session(title=request.title)
    await repo.add(session)
    return SessionResponse(session_id=session.id, title=session.title, history=[])

@router.get("/history", response_model=SessionResponse)
async def get_history(
    session_id: str,
    repo: SessionRepository = Depends(get_session_repo)
):
    session = await repo.get_with_history(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    history = [
        ChatMessage(role=msg.role, content=msg.content, created_at=msg.created_at)
        for msg in session.history
    ]
    return SessionResponse(session_id=session.id, title=session.title, history=history)
