from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.repositories.base_repo import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Asset)
