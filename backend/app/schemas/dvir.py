import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DVIRReportBase(BaseModel):
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    inspection_type: str  # pre_trip | post_trip
    defects_count: int = 0
    notes: str | None = None
    passed: bool = True


class DVIRReportCreate(DVIRReportBase):
    pass


class DVIRReportRead(DVIRReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    submitted_at: datetime
