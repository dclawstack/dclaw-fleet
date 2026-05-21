import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accident import AccidentReport
from app.repositories.base_repo import BaseRepository


class AccidentRepository(BaseRepository[AccidentReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AccidentReport)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[AccidentReport]:
        result = await self.db.execute(
            select(AccidentReport)
            .where(AccidentReport.vehicle_id == vehicle_id)
            .order_by(desc(AccidentReport.occurred_at))
        )
        return list(result.scalars().all())

    async def open_claims(self) -> list[AccidentReport]:
        result = await self.db.execute(
            select(AccidentReport)
            .where(AccidentReport.claim_status == "open")
            .order_by(desc(AccidentReport.occurred_at))
        )
        return list(result.scalars().all())
