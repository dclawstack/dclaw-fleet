from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.part import Part
from app.repositories.base_repo import BaseRepository


class PartRepository(BaseRepository[Part]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Part)

    async def low_stock(self) -> list[Part]:
        result = await self.db.execute(
            select(Part).where(Part.stock <= Part.reorder_threshold).order_by(Part.name)
        )
        return list(result.scalars().all())
