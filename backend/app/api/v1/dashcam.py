import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.dashcam import DashcamEvent
from app.repositories.dashcam_repo import DashcamRepository
from app.schemas.dashcam import DashcamEventCreate, DashcamEventRead

router = APIRouter()


@router.get("", response_model=list[DashcamEventRead])
async def list_events(db: AsyncSession = Depends(get_db)):
    repo = DashcamRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [DashcamEventRead.model_validate(e) for e in items]


@router.post("", response_model=DashcamEventRead, status_code=status.HTTP_201_CREATED)
async def create_event(payload: DashcamEventCreate, db: AsyncSession = Depends(get_db)):
    repo = DashcamRepository(db)
    event = DashcamEvent(**payload.model_dump())
    created = await repo.create(event)
    return DashcamEventRead.model_validate(created)


@router.get("/vehicles/{vehicle_id}", response_model=list[DashcamEventRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DashcamRepository(db)
    items = await repo.for_vehicle(vehicle_id)
    return [DashcamEventRead.model_validate(e) for e in items]
