from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.orm import Session, ConversationHistory

class SessionRepository(BaseRepository[Session]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_with_history(self, session_id: str) -> Optional[Session]:
        result = await self.session.execute(
            select(Session)
            .options(selectinload(Session.history))
            .where(Session.id == session_id)
        )
        return result.scalars().first()

    async def add_message(self, session_id: str, role: str, content: str) -> ConversationHistory:
        msg = ConversationHistory(session_id=session_id, role=role, content=content)
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg
