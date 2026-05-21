import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelematicsDeviceCreate(BaseModel):
    vehicle_id: uuid.UUID
    vendor: str
    device_id: str
    status: str = "active"


class TelematicsDeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    vendor: str
    device_id: str
    status: str
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TelematicsHeartbeat(BaseModel):
    device_id: str
    timestamp: datetime | None = None
    payload: dict | None = None  # opaque vendor blob


class TelematicsHeartbeatResult(BaseModel):
    device_id: str
    vehicle_id: uuid.UUID
    anomalies: list[str]
