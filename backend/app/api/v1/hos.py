import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.hos import HOSLog
from app.repositories.hos_repo import HOSRepository
from app.schemas.hos import HOSLogCreate, HOSLogRead, HOSStatus
from app.services.compliance import hos_status_for_driver

router = APIRouter()


@router.post("", response_model=HOSLogRead, status_code=status.HTTP_201_CREATED)
async def create_log(payload: HOSLogCreate, db: AsyncSession = Depends(get_db)):
    repo = HOSRepository(db)
    data = payload.model_dump()
    if data.get("started_at") is None:
        data["started_at"] = datetime.now(timezone.utc)

    current = await repo.current_for_driver(payload.driver_id)
    if current and current.ended_at is None:
        await repo.update(current, {"ended_at": data["started_at"]})

    log = HOSLog(**data)
    created = await repo.create(log)
    return HOSLogRead.model_validate(created)


@router.get("/drivers/{driver_id}", response_model=list[HOSLogRead])
async def for_driver(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = HOSRepository(db)
    logs = await repo.for_driver(driver_id)
    return [HOSLogRead.model_validate(l) for l in logs]


@router.get("/drivers/{driver_id}/status", response_model=HOSStatus)
async def driver_status(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await hos_status_for_driver(db, driver_id)
