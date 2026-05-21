from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permit import Permit
from app.repositories.base_repo import BaseRepository


class PermitRepository(BaseRepository[Permit]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permit)

    async def expired(self, today: date | None = None) -> list[Permit]:
        today = today or date.today()
        result = await self.db.execute(
            select(Permit)
            .where(Permit.expiry_date < today)
            .order_by(Permit.expiry_date)
        )
        return list(result.scalars().all())

    async def expiring_within(self, days: int = 30, today: date | None = None) -> list[Permit]:
        today = today or date.today()
        cutoff = today + timedelta(days=days)
        result = await self.db.execute(
            select(Permit)
            .where(Permit.expiry_date >= today)
            .where(Permit.expiry_date <= cutoff)
            .order_by(Permit.expiry_date)
        )
        return list(result.scalars().all())
