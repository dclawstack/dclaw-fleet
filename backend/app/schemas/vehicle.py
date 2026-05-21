import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    vin: str
    license_plate: str
    make: str
    model: str
    year: int
    status: str = "active"
    fuel_type: str = "gasoline"
    odometer_miles: int = 0
    engine_hours: int = 0
    driver_id: uuid.UUID | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    license_plate: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    status: str | None = None
    fuel_type: str | None = None
    odometer_miles: int | None = None
    engine_hours: int | None = None
    driver_id: uuid.UUID | None = None


class VehicleRead(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
