import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LocationPingCreate(BaseModel):
    vehicle_id: uuid.UUID
    lat: float
    lng: float
    speed_mph: float = 0.0
    heading_deg: float = 0.0


class LocationPingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    lat: float
    lng: float
    speed_mph: float
    heading_deg: float
    recorded_at: datetime


class GeofenceBreachAlert(BaseModel):
    vehicle_id: uuid.UUID
    geofence_id: uuid.UUID
    geofence_name: str
    fence_type: str
    breach_type: str
    distance_m: float
