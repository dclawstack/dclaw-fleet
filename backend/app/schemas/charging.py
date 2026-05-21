import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChargingSessionCreate(BaseModel):
    vehicle_id: uuid.UUID
    station_id: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    energy_kwh: float = 0.0
    cost: float = 0.0
    soc_start: float | None = None
    soc_end: float | None = None


class ChargingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    station_id: str | None
    started_at: datetime
    ended_at: datetime | None
    energy_kwh: float
    cost: float
    soc_start: float | None
    soc_end: float | None


class RangePrediction(BaseModel):
    vehicle_id: uuid.UUID
    current_soc: float | None
    estimated_range_miles: float
    confidence: str  # low | medium | high
    notes: list[str]


class ChargeRecommendation(BaseModel):
    vehicle_id: uuid.UUID
    needs_charge: bool
    target_soc: float
    suggested_window: str
    reason: str
