import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RouteStopBase(BaseModel):
    sequence: int
    address: str
    lat: float
    lng: float


class RouteStopRead(RouteStopBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    route_id: uuid.UUID


class RouteBase(BaseModel):
    name: str
    status: str = "draft"
    vehicle_id: uuid.UUID | None = None


class RouteCreate(RouteBase):
    stops: list[RouteStopBase] = []


class RouteUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    vehicle_id: uuid.UUID | None = None


class RouteRead(RouteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    optimized_distance_miles: float | None
    optimized_duration_min: int | None
    stops: list[RouteStopRead]
    created_at: datetime
    updated_at: datetime


class RouteOptimizeResult(BaseModel):
    route_id: uuid.UUID
    optimized_sequence: list[uuid.UUID]
    total_distance_miles: float
    total_duration_min: int
