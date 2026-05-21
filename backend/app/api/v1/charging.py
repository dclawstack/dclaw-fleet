import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.charging import ChargingSession
from app.repositories.charging_repo import ChargingRepository
from app.schemas.charging import (
    ChargeRecommendation,
    ChargingSessionCreate,
    ChargingSessionRead,
    RangePrediction,
)
from app.services.ev import charge_recommendation, ensure_vehicle, predict_range

router = APIRouter()


@router.get("", response_model=list[ChargingSessionRead])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    repo = ChargingRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [ChargingSessionRead.model_validate(s) for s in items]


@router.post("", response_model=ChargingSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(payload: ChargingSessionCreate, db: AsyncSession = Depends(get_db)):
    if not await ensure_vehicle(db, payload.vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    repo = ChargingRepository(db)
    data = payload.model_dump()
    if data.get("started_at") is None:
        data["started_at"] = datetime.now(timezone.utc)
    session = ChargingSession(**data)
    created = await repo.create(session)
    return ChargingSessionRead.model_validate(created)


@router.get("/vehicles/{vehicle_id}", response_model=list[ChargingSessionRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ChargingRepository(db)
    items = await repo.for_vehicle(vehicle_id)
    return [ChargingSessionRead.model_validate(s) for s in items]


@router.get("/vehicles/{vehicle_id}/range", response_model=RangePrediction)
async def range_prediction(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await ensure_vehicle(db, vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await predict_range(db, vehicle_id)


@router.get("/vehicles/{vehicle_id}/recommendation", response_model=ChargeRecommendation)
async def recommendation(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await ensure_vehicle(db, vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await charge_recommendation(db, vehicle_id)
