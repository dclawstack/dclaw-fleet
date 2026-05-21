import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DashcamEventBase(BaseModel):
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    event_type: str  # collision | distraction | lane_drift | hard_corner | tailgating
    severity: int = Field(default=5, ge=1, le=10)
    video_url: str | None = None


class DashcamEventCreate(DashcamEventBase):
    pass


class DashcamEventRead(DashcamEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recorded_at: datetime
