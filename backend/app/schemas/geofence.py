import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GeofenceBase(BaseModel):
    name: str
    fence_type: str = "inclusion"
    center_lat: float
    center_lng: float
    radius_m: float


class GeofenceCreate(GeofenceBase):
    pass


class GeofenceUpdate(BaseModel):
    name: str | None = None
    fence_type: str | None = None
    center_lat: float | None = None
    center_lng: float | None = None
    radius_m: float | None = None


class GeofenceRead(GeofenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
