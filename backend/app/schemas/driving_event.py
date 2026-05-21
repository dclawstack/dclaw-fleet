import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DrivingEventBase(BaseModel):
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    event_type: str  # harsh_brake | harsh_accel | speeding | idle | harsh_turn
    severity: int = Field(default=5, ge=1, le=10)
    lat: float | None = None
    lng: float | None = None


class DrivingEventCreate(DrivingEventBase):
    pass


class DrivingEventRead(DrivingEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recorded_at: datetime


class DriverScore(BaseModel):
    driver_id: uuid.UUID
    score: int
    event_count: int
    events_by_type: dict[str, int]


class CoachingTip(BaseModel):
    event_type: str
    severity: str  # info | warning | critical
    message: str


class DriverCoaching(BaseModel):
    driver_id: uuid.UUID
    score: int
    tips: list[CoachingTip]
