import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HOSLogBase(BaseModel):
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID | None = None
    duty_status: str  # driving | on_duty | sleeper | off_duty
    started_at: datetime | None = None
    ended_at: datetime | None = None
    miles: float = 0.0


class HOSLogCreate(HOSLogBase):
    pass


class HOSLogRead(HOSLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    started_at: datetime


class HOSStatus(BaseModel):
    driver_id: uuid.UUID
    current_status: str
    on_duty_hours_today: float
    driving_hours_today: float
    remaining_drive_hours: float
    remaining_duty_hours: float
    violations: list[str]
