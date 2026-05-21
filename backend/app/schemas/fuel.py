import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FuelLogBase(BaseModel):
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    gallons: float
    cost: float
    odometer_miles: int
    fuel_type: str = "gasoline"
    filled_at: datetime | None = None


class FuelLogCreate(FuelLogBase):
    pass


class FuelLogUpdate(BaseModel):
    gallons: float | None = None
    cost: float | None = None
    odometer_miles: int | None = None
    fuel_type: str | None = None


class FuelLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID | None
    gallons: float
    cost: float
    odometer_miles: int
    fuel_type: str
    filled_at: datetime
    created_at: datetime
    updated_at: datetime


class FuelEfficiencyReport(BaseModel):
    vehicle_id: uuid.UUID
    total_gallons: float
    total_cost: float
    total_miles: int
    mpg: float | None
    anomalies: list[str]
