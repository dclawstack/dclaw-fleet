import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charging import ChargingSession
from app.repositories.base_repo import BaseRepository


class ChargingRepository(BaseRepository[ChargingSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ChargingSession)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[ChargingSession]:
        result = await self.db.execute(
            select(ChargingSession)
            .where(ChargingSession.vehicle_id == vehicle_id)
            .order_by(desc(ChargingSession.started_at))
        )
        return list(result.scalars().all())

    async def latest_for_vehicle(self, vehicle_id: uuid.UUID) -> ChargingSession | None:
        result = await self.db.execute(
            select(ChargingSession)
            .where(ChargingSession.vehicle_id == vehicle_id)
            .order_by(desc(ChargingSession.started_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
