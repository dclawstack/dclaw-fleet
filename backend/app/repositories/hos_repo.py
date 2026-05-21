import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hos import HOSLog
from app.repositories.base_repo import BaseRepository


class HOSRepository(BaseRepository[HOSLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, HOSLog)

    async def for_driver(self, driver_id: uuid.UUID, since: datetime | None = None) -> list[HOSLog]:
        q = select(HOSLog).where(HOSLog.driver_id == driver_id)
        if since is not None:
            q = q.where(HOSLog.started_at >= since)
        q = q.order_by(desc(HOSLog.started_at))
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def current_for_driver(self, driver_id: uuid.UUID) -> HOSLog | None:
        result = await self.db.execute(
            select(HOSLog)
            .where(HOSLog.driver_id == driver_id)
            .where(HOSLog.ended_at.is_(None))
            .order_by(desc(HOSLog.started_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
