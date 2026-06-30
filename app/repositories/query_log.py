from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.orm import QueryLog

class QueryLogRepository(BaseRepository[QueryLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QueryLog)
