import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import LocationPing
from app.repositories.base_repo import BaseRepository


class LocationRepository(BaseRepository[LocationPing]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LocationPing)

    async def latest_for_vehicle(self, vehicle_id: uuid.UUID) -> LocationPing | None:
        result = await self.db.execute(
            select(LocationPing)
            .where(LocationPing.vehicle_id == vehicle_id)
            .order_by(desc(LocationPing.recorded_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def latest_per_vehicle(self) -> list[LocationPing]:
        subq = (
            select(
                LocationPing.vehicle_id,
                LocationPing.id,
                LocationPing.recorded_at,
            )
            .order_by(LocationPing.vehicle_id, desc(LocationPing.recorded_at))
            .distinct(LocationPing.vehicle_id)
            .subquery()
        )
        result = await self.db.execute(
            select(LocationPing).join(subq, LocationPing.id == subq.c.id)
        )
        return list(result.scalars().all())

    async def history_for_vehicle(
        self, vehicle_id: uuid.UUID, limit: int = 100
    ) -> list[LocationPing]:
        result = await self.db.execute(
            select(LocationPing)
            .where(LocationPing.vehicle_id == vehicle_id)
            .order_by(desc(LocationPing.recorded_at))
            .limit(limit)
        )
        return list(result.scalars().all())
