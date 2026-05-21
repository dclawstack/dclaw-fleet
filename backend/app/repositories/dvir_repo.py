import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dvir import DVIRReport
from app.repositories.base_repo import BaseRepository


class DVIRRepository(BaseRepository[DVIRReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DVIRReport)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[DVIRReport]:
        result = await self.db.execute(
            select(DVIRReport)
            .where(DVIRReport.vehicle_id == vehicle_id)
            .order_by(desc(DVIRReport.submitted_at))
        )
        return list(result.scalars().all())

    async def failed_since(self, since: datetime) -> list[DVIRReport]:
        result = await self.db.execute(
            select(DVIRReport)
            .where(DVIRReport.passed.is_(False))
            .where(DVIRReport.submitted_at >= since)
            .order_by(desc(DVIRReport.submitted_at))
        )
        return list(result.scalars().all())
