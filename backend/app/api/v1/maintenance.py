import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.maintenance import MaintenanceTask
from app.repositories.maintenance_repo import MaintenanceRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.common import Page, PageMeta
from app.schemas.maintenance import (
    MaintenanceTaskCreate,
    MaintenanceTaskRead,
    MaintenanceTaskUpdate,
)
from app.services.maintenance import (
    auto_schedule_for_vehicle,
    scan_overdue,
    vehicle_health_score,
)

router = APIRouter()


@router.get("", response_model=Page[MaintenanceTaskRead])
async def list_tasks(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = MaintenanceRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[MaintenanceTaskRead](
        items=[MaintenanceTaskRead.model_validate(t) for t in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=MaintenanceTaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: MaintenanceTaskCreate, db: AsyncSession = Depends(get_db)):
    repo = MaintenanceRepository(db)
    task = MaintenanceTask(**payload.model_dump())
    created = await repo.create(task)
    return MaintenanceTaskRead.model_validate(created)


@router.get("/overdue", response_model=list[MaintenanceTaskRead])
async def list_overdue(db: AsyncSession = Depends(get_db)):
    tasks = await scan_overdue(db)
    return [MaintenanceTaskRead.model_validate(t) for t in tasks]


@router.get("/vehicles/{vehicle_id}", response_model=list[MaintenanceTaskRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = MaintenanceRepository(db)
    tasks = await repo.for_vehicle(vehicle_id)
    return [MaintenanceTaskRead.model_validate(t) for t in tasks]


@router.post("/vehicles/{vehicle_id}/auto-schedule", response_model=MaintenanceTaskRead | None)
async def auto_schedule(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    v_repo = VehicleRepository(db)
    vehicle = await v_repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    task = await auto_schedule_for_vehicle(db, vehicle)
    return MaintenanceTaskRead.model_validate(task) if task else None


@router.get("/vehicles/{vehicle_id}/health-score")
async def health_score(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    v_repo = VehicleRepository(db)
    vehicle = await v_repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    score = await vehicle_health_score(db, vehicle)
    return {"vehicle_id": str(vehicle_id), "health_score": score}


@router.patch("/{task_id}", response_model=MaintenanceTaskRead)
async def update_task(
    task_id: uuid.UUID,
    payload: MaintenanceTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = MaintenanceRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = await repo.update(task, payload.model_dump(exclude_unset=True))
    return MaintenanceTaskRead.model_validate(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = MaintenanceRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await repo.delete(task)
