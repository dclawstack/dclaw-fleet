from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telematics import TelematicsDevice
from app.repositories.base_repo import BaseRepository


class TelematicsRepository(BaseRepository[TelematicsDevice]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, TelematicsDevice)

    async def by_device_id(self, device_id: str) -> TelematicsDevice | None:
        result = await self.db.execute(
            select(TelematicsDevice).where(TelematicsDevice.device_id == device_id)
        )
        return result.scalar_one_or_none()
