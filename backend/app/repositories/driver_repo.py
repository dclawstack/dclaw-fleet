from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.repositories.base_repo import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Driver)
