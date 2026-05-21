import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fuel import FuelLog
from app.repositories.base_repo import BaseRepository


class FuelRepository(BaseRepository[FuelLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, FuelLog)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[FuelLog]:
        result = await self.db.execute(
            select(FuelLog)
            .where(FuelLog.vehicle_id == vehicle_id)
            .order_by(desc(FuelLog.filled_at))
        )
        return list(result.scalars().all())
