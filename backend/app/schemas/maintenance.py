import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MaintenanceTaskBase(BaseModel):
    vehicle_id: uuid.UUID
    task_type: str
    description: str | None = None
    due_date: date | None = None
    due_mileage: int | None = None
    status: str = "scheduled"
    completed_date: date | None = None
    cost: float | None = None


class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass


class MaintenanceTaskUpdate(BaseModel):
    task_type: str | None = None
    description: str | None = None
    due_date: date | None = None
    due_mileage: int | None = None
    status: str | None = None
    completed_date: date | None = None
    cost: float | None = None


class MaintenanceTaskRead(MaintenanceTaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
