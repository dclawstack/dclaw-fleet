import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PermitBase(BaseModel):
    entity_type: str  # vehicle | driver
    entity_id: uuid.UUID
    permit_type: str
    issuer: str | None = None
    permit_number: str
    issued_date: date | None = None
    expiry_date: date
    status: str = "active"


class PermitCreate(PermitBase):
    pass


class PermitUpdate(BaseModel):
    permit_type: str | None = None
    issuer: str | None = None
    permit_number: str | None = None
    issued_date: date | None = None
    expiry_date: date | None = None
    status: str | None = None


class PermitRead(PermitBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ComplianceSummary(BaseModel):
    expired_permits: int
    expiring_soon: int  # within 30 days
    failed_dvir: int  # in last 30 days
    hos_violations: int
