import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.location_repo import LocationRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.location import (
    GeofenceBreachAlert,
    LocationPingCreate,
    LocationPingRead,
)
from app.services.tracking import record_ping

router = APIRouter()


class IngestResponse(BaseModel):
    ping: LocationPingRead
    breach_alerts: list[GeofenceBreachAlert]


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_ping(payload: LocationPingCreate, db: AsyncSession = Depends(get_db)):
    v_repo = VehicleRepository(db)
    if not await v_repo.get_by_id(payload.vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    ping, alerts = await record_ping(
        db,
        vehicle_id=payload.vehicle_id,
        lat=payload.lat,
        lng=payload.lng,
        speed_mph=payload.speed_mph,
        heading_deg=payload.heading_deg,
    )
    return IngestResponse(
        ping=LocationPingRead.model_validate(ping),
        breach_alerts=alerts,
    )


@router.get("/latest", response_model=list[LocationPingRead])
async def latest_per_vehicle(db: AsyncSession = Depends(get_db)):
    repo = LocationRepository(db)
    pings = await repo.latest_per_vehicle()
    return [LocationPingRead.model_validate(p) for p in pings]


@router.get("/vehicles/{vehicle_id}/history", response_model=list[LocationPingRead])
async def vehicle_history(
    vehicle_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    repo = LocationRepository(db)
    pings = await repo.history_for_vehicle(vehicle_id, limit=limit)
    return [LocationPingRead.model_validate(p) for p in pings]
