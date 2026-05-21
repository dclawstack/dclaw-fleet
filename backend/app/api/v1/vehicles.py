import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.common import Page, PageMeta
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter()


@router.get("", response_model=Page[VehicleRead])
async def list_vehicles(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = VehicleRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[VehicleRead](
        items=[VehicleRead.model_validate(v) for v in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    vehicle = Vehicle(**payload.model_dump())
    created = await repo.create(vehicle)
    return VehicleRead.model_validate(created)


@router.get("/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleRead.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = VehicleRepository(db)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    updated = await repo.update(vehicle, payload.model_dump(exclude_unset=True))
    return VehicleRead.model_validate(updated)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await repo.delete(vehicle)
