import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccidentReportBase(BaseModel):
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    occurred_at: datetime | None = None
    severity_score: int = Field(default=1, ge=1, le=10)
    photos_count: int = 0
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    claim_status: str = "open"
    claim_amount: float = 0.0


class AccidentReportCreate(AccidentReportBase):
    pass


class AccidentReportUpdate(BaseModel):
    severity_score: int | None = None
    photos_count: int | None = None
    description: str | None = None
    claim_status: str | None = None
    claim_amount: float | None = None


class AccidentReportRead(AccidentReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    predicted_claim_amount: float | None
    created_at: datetime
    updated_at: datetime
