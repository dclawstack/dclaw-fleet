from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geofence import Geofence
from app.repositories.base_repo import BaseRepository


class GeofenceRepository(BaseRepository[Geofence]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Geofence)
