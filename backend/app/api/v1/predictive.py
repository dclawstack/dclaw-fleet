import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.predictive import (
    AutonomousDispatchResult,
    CarbonReport,
    PredictiveReport,
)
from app.services.autonomous_dispatch import plan as dispatch_plan
from app.services.carbon import carbon_for_vehicle, fleet_carbon
from app.services.predictive_maintenance import predict

router = APIRouter()


@router.get("/maintenance/vehicles/{vehicle_id}", response_model=PredictiveReport)
async def maintenance_prediction(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    if not await repo.get_by_id(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await predict(db, vehicle_id)


@router.get("/carbon/vehicles/{vehicle_id}", response_model=CarbonReport)
async def carbon_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    if not await repo.get_by_id(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await carbon_for_vehicle(db, vehicle_id)


@router.get("/carbon/fleet", response_model=CarbonReport)
async def carbon_fleet(db: AsyncSession = Depends(get_db)):
    return await fleet_carbon(db)


@router.post("/dispatch/plan", response_model=AutonomousDispatchResult)
async def dispatch(db: AsyncSession = Depends(get_db)):
    return await dispatch_plan(db)
