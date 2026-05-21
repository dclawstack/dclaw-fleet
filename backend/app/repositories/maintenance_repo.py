import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance import MaintenanceTask
from app.repositories.base_repo import BaseRepository


class MaintenanceRepository(BaseRepository[MaintenanceTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, MaintenanceTask)

    async def for_vehicle(self, vehicle_id: uuid.UUID) -> list[MaintenanceTask]:
        result = await self.db.execute(
            select(MaintenanceTask)
            .where(MaintenanceTask.vehicle_id == vehicle_id)
            .order_by(MaintenanceTask.due_date.asc().nullslast())
        )
        return list(result.scalars().all())

    async def overdue(self, today) -> list[MaintenanceTask]:
        result = await self.db.execute(
            select(MaintenanceTask)
            .where(MaintenanceTask.status != "completed")
            .where(MaintenanceTask.due_date.is_not(None))
            .where(MaintenanceTask.due_date < today)
        )
        return list(result.scalars().all())
