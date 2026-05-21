import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class DriverBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    license_number: str
    license_expiry: date | None = None
    status: str = "active"
    safety_score: int = 100


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    license_number: str | None = None
    license_expiry: date | None = None
    status: str | None = None
    safety_score: int | None = None


class DriverRead(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
