import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driving_event import DrivingEvent
from app.repositories.base_repo import BaseRepository


class DrivingEventRepository(BaseRepository[DrivingEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DrivingEvent)

    async def for_driver(self, driver_id: uuid.UUID, since: datetime | None = None) -> list[DrivingEvent]:
        q = select(DrivingEvent).where(DrivingEvent.driver_id == driver_id)
        if since is not None:
            q = q.where(DrivingEvent.recorded_at >= since)
        q = q.order_by(desc(DrivingEvent.recorded_at))
        result = await self.db.execute(q)
        return list(result.scalars().all())
