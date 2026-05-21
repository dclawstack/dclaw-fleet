import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.driver import Driver
from app.repositories.driver_repo import DriverRepository
from app.schemas.common import Page, PageMeta
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate

router = APIRouter()


@router.get("", response_model=Page[DriverRead])
async def list_drivers(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = DriverRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[DriverRead](
        items=[DriverRead.model_validate(d) for d in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def create_driver(payload: DriverCreate, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = Driver(**payload.model_dump())
    created = await repo.create(driver)
    return DriverRead.model_validate(created)


@router.get("/{driver_id}", response_model=DriverRead)
async def get_driver(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return DriverRead.model_validate(driver)


@router.patch("/{driver_id}", response_model=DriverRead)
async def update_driver(
    driver_id: uuid.UUID,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    updated = await repo.update(driver, payload.model_dump(exclude_unset=True))
    return DriverRead.model_validate(updated)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(driver_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    await repo.delete(driver)
