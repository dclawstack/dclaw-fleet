import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.geofence import Geofence
from app.repositories.geofence_repo import GeofenceRepository
from app.schemas.common import Page, PageMeta
from app.schemas.geofence import GeofenceCreate, GeofenceRead, GeofenceUpdate

router = APIRouter()


@router.get("", response_model=Page[GeofenceRead])
async def list_geofences(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = GeofenceRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[GeofenceRead](
        items=[GeofenceRead.model_validate(g) for g in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=GeofenceRead, status_code=status.HTTP_201_CREATED)
async def create_geofence(payload: GeofenceCreate, db: AsyncSession = Depends(get_db)):
    repo = GeofenceRepository(db)
    fence = Geofence(**payload.model_dump())
    created = await repo.create(fence)
    return GeofenceRead.model_validate(created)


@router.get("/{geofence_id}", response_model=GeofenceRead)
async def get_geofence(geofence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = GeofenceRepository(db)
    fence = await repo.get_by_id(geofence_id)
    if not fence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    return GeofenceRead.model_validate(fence)


@router.patch("/{geofence_id}", response_model=GeofenceRead)
async def update_geofence(
    geofence_id: uuid.UUID,
    payload: GeofenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = GeofenceRepository(db)
    fence = await repo.get_by_id(geofence_id)
    if not fence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    updated = await repo.update(fence, payload.model_dump(exclude_unset=True))
    return GeofenceRead.model_validate(updated)


@router.delete("/{geofence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_geofence(geofence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = GeofenceRepository(db)
    fence = await repo.get_by_id(geofence_id)
    if not fence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    await repo.delete(fence)
