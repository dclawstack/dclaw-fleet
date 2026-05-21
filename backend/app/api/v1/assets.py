import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.repositories.asset_repo import AssetRepository
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.schemas.common import Page, PageMeta

router = APIRouter()


@router.get("", response_model=Page[AssetRead])
async def list_assets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[AssetRead](
        items=[AssetRead.model_validate(a) for a in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(payload: AssetCreate, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = Asset(**payload.model_dump())
    created = await repo.create(asset)
    return AssetRead.model_validate(created)


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetRead.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    updated = await repo.update(asset, payload.model_dump(exclude_unset=True))
    return AssetRead.model_validate(updated)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await repo.delete(asset)
