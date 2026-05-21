import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.driving_event import DrivingEvent
from app.repositories.driver_repo import DriverRepository
from app.repositories.driving_event_repo import DrivingEventRepository
from app.schemas.driving_event import (
    DriverCoaching,
    DriverScore,
    DrivingEventCreate,
    DrivingEventRead,
)
from app.services.driver_scoring import (
    coaching_tips,
    persist_driver_safety_score,
    score_driver,
)

router = APIRouter()


@router.post("", response_model=DrivingEventRead, status_code=status.HTTP_201_CREATED)
async def ingest_event(payload: DrivingEventCreate, db: AsyncSession = Depends(get_db)):
    repo = DrivingEventRepository(db)
    event = DrivingEvent(**payload.model_dump())
    created = await repo.create(event)
    return DrivingEventRead.model_validate(created)


@router.get("", response_model=list[DrivingEventRead])
async def list_events(
    driver_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    repo = DrivingEventRepository(db)
    if driver_id is not None:
        events = await repo.for_driver(driver_id)
    else:
        events, _ = await repo.list_all(limit=200)
    return [DrivingEventRead.model_validate(e) for e in events]


@router.get("/drivers/{driver_id}/score", response_model=DriverScore)
async def driver_score(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    d_repo = DriverRepository(db)
    if not await d_repo.get_by_id(driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    return await score_driver(db, driver_id)


@router.get("/drivers/{driver_id}/coaching", response_model=DriverCoaching)
async def driver_coaching(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    d_repo = DriverRepository(db)
    if not await d_repo.get_by_id(driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    return await coaching_tips(db, driver_id)


@router.post("/drivers/{driver_id}/recompute-score")
async def recompute_safety_score(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    d_repo = DriverRepository(db)
    if not await d_repo.get_by_id(driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    score = await persist_driver_safety_score(db, driver_id)
    return {"driver_id": str(driver_id), "safety_score": score}
