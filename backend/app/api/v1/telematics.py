from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.telematics import TelematicsDevice
from app.repositories.telematics_repo import TelematicsRepository
from app.schemas.telematics import (
    TelematicsDeviceCreate,
    TelematicsDeviceRead,
    TelematicsHeartbeat,
    TelematicsHeartbeatResult,
)
from app.services.telematics import ingest_heartbeat

router = APIRouter()


@router.get("/devices", response_model=list[TelematicsDeviceRead])
async def list_devices(db: AsyncSession = Depends(get_db)):
    repo = TelematicsRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [TelematicsDeviceRead.model_validate(d) for d in items]


@router.post("/devices", response_model=TelematicsDeviceRead, status_code=status.HTTP_201_CREATED)
async def register_device(payload: TelematicsDeviceCreate, db: AsyncSession = Depends(get_db)):
    repo = TelematicsRepository(db)
    device = TelematicsDevice(**payload.model_dump())
    created = await repo.create(device)
    return TelematicsDeviceRead.model_validate(created)


@router.post("/heartbeat", response_model=TelematicsHeartbeatResult)
async def heartbeat(payload: TelematicsHeartbeat, db: AsyncSession = Depends(get_db)):
    try:
        return await ingest_heartbeat(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
