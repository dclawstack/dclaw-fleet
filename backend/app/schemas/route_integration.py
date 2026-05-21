import uuid
from datetime import datetime

from pydantic import BaseModel


class RouteSyncResult(BaseModel):
    synced_count: int
    failed_count: int
    synced_route_ids: list[uuid.UUID]
    synced_at: datetime


class RouteAssignment(BaseModel):
    route_id: uuid.UUID
    vehicle_id: uuid.UUID | None
    vehicle_plate: str | None
    reason: str


class AutoAssignResult(BaseModel):
    assignments: list[RouteAssignment]
    skipped_count: int
    skipped_reasons: list[str]
