import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_chat import AIChatMessage, AIChatSession
from app.repositories.base_repo import BaseRepository


class AIChatSessionRepository(BaseRepository[AIChatSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AIChatSession)

    async def with_messages(self, session_id: uuid.UUID) -> AIChatSession | None:
        result = await self.db.execute(
            select(AIChatSession).where(AIChatSession.id == session_id)
        )
        return result.scalar_one_or_none()


class AIChatMessageRepository(BaseRepository[AIChatMessage]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AIChatMessage)

    async def for_session(self, session_id: uuid.UUID) -> list[AIChatMessage]:
        result = await self.db.execute(
            select(AIChatMessage)
            .where(AIChatMessage.session_id == session_id)
            .order_by(AIChatMessage.created_at)
        )
        return list(result.scalars().all())
