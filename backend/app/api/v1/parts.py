import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.part import Part
from app.repositories.part_repo import PartRepository
from app.schemas.part import (
    PartCreate,
    PartRead,
    PartUpdate,
    ReorderRecommendation,
)
from app.services.parts import reorder_recommendations

router = APIRouter()


@router.get("", response_model=list[PartRead])
async def list_parts(db: AsyncSession = Depends(get_db)):
    repo = PartRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [PartRead.model_validate(p) for p in items]


@router.post("", response_model=PartRead, status_code=status.HTTP_201_CREATED)
async def create_part(payload: PartCreate, db: AsyncSession = Depends(get_db)):
    repo = PartRepository(db)
    part = Part(**payload.model_dump())
    created = await repo.create(part)
    return PartRead.model_validate(created)


@router.get("/low-stock", response_model=list[PartRead])
async def low_stock(db: AsyncSession = Depends(get_db)):
    repo = PartRepository(db)
    items = await repo.low_stock()
    return [PartRead.model_validate(p) for p in items]


@router.get("/reorder-recommendations", response_model=list[ReorderRecommendation])
async def recommendations(db: AsyncSession = Depends(get_db)):
    return await reorder_recommendations(db)


@router.patch("/{part_id}", response_model=PartRead)
async def update_part(
    part_id: uuid.UUID,
    payload: PartUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = PartRepository(db)
    part = await repo.get_by_id(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    updated = await repo.update(part, payload.model_dump(exclude_unset=True))
    return PartRead.model_validate(updated)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(part_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PartRepository(db)
    part = await repo.get_by_id(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    await repo.delete(part)
