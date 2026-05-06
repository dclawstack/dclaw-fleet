import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CreateStatusRequest(BaseModel):
    fleet_id: str


class FleetStatus(BaseModel):
    id: str
    fleet_id: str
    active_vehicles: int
    avg_fuel_efficiency: int
    maintenance_due_count: int
    route_compliance_percent: int
    created_at: str


class VehicleStatus(BaseModel):
    vehicle_id: str
    driver: str
    status: str
    location: str


@router.post("/statuses")
async def create_status(req: CreateStatusRequest) -> FleetStatus:
    return FleetStatus(
        id=str(uuid.uuid4()),
        fleet_id=req.fleet_id,
        active_vehicles=random.randint(10, 100),
        avg_fuel_efficiency=random.randint(6, 12),
        maintenance_due_count=random.randint(0, 5),
        route_compliance_percent=random.randint(85, 99),
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


@router.get("/statuses/{status_id}/vehicles")
async def get_status_vehicles(status_id: str) -> list[VehicleStatus]:
    return [
        VehicleStatus(vehicle_id="VH-001", driver="John Doe", status="En route", location="Highway 101"),
        VehicleStatus(vehicle_id="VH-002", driver="Jane Smith", status="Idle", location="Depot A"),
        VehicleStatus(vehicle_id="VH-003", driver="Bob Lee", status="Loading", location="Warehouse 3"),
    ]
