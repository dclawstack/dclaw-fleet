import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.fuel import FuelLog
from app.repositories.fuel_repo import FuelRepository
from app.schemas.common import Page, PageMeta
from app.schemas.fuel import (
    FuelEfficiencyReport,
    FuelLogCreate,
    FuelLogRead,
    FuelLogUpdate,
)
from app.services.fuel import efficiency_report

router = APIRouter()


@router.get("", response_model=Page[FuelLogRead])
async def list_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = FuelRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[FuelLogRead](
        items=[FuelLogRead.model_validate(l) for l in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=FuelLogRead, status_code=status.HTTP_201_CREATED)
async def create_log(payload: FuelLogCreate, db: AsyncSession = Depends(get_db)):
    repo = FuelRepository(db)
    data = payload.model_dump()
    if data.get("filled_at") is None:
        data["filled_at"] = datetime.now(timezone.utc)
    log = FuelLog(**data)
    created = await repo.create(log)
    return FuelLogRead.model_validate(created)


@router.get("/vehicles/{vehicle_id}", response_model=list[FuelLogRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FuelRepository(db)
    logs = await repo.for_vehicle(vehicle_id)
    return [FuelLogRead.model_validate(l) for l in logs]


@router.get("/vehicles/{vehicle_id}/report", response_model=FuelEfficiencyReport)
async def report(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await efficiency_report(db, vehicle_id)


@router.patch("/{log_id}", response_model=FuelLogRead)
async def update_log(
    log_id: uuid.UUID,
    payload: FuelLogUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = FuelRepository(db)
    log = await repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Fuel log not found")
    updated = await repo.update(log, payload.model_dump(exclude_unset=True))
    return FuelLogRead.model_validate(updated)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FuelRepository(db)
    log = await repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Fuel log not found")
    await repo.delete(log)
