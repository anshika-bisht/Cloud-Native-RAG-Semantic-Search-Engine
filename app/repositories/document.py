from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.orm import Document, Chunk

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_by_hash(self, content_hash: str) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.content_hash == content_hash)
        )
        return result.scalars().first()
        
    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[Chunk]:
        if not chunk_ids:
            return []
        result = await self.session.execute(
            select(Chunk).where(Chunk.id.in_(chunk_ids))
        )
        return result.scalars().all()

    async def add_chunks(self, chunks: List[Chunk]) -> None:
        self.session.add_all(chunks)
        await self.session.commit()
