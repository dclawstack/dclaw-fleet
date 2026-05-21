import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashcam import DashcamEvent
from app.repositories.base_repo import BaseRepository


class DashcamRepository(BaseRepository[DashcamEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DashcamEvent)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[DashcamEvent]:
        result = await self.db.execute(
            select(DashcamEvent)
            .where(DashcamEvent.vehicle_id == vehicle_id)
            .order_by(desc(DashcamEvent.recorded_at))
        )
        return list(result.scalars().all())
