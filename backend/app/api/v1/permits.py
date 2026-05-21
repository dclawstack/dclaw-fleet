import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.permit import Permit
from app.repositories.permit_repo import PermitRepository
from app.schemas.permit import (
    ComplianceSummary,
    PermitCreate,
    PermitRead,
    PermitUpdate,
)
from app.services.compliance import compliance_summary

router = APIRouter()


@router.get("", response_model=list[PermitRead])
async def list_permits(db: AsyncSession = Depends(get_db)):
    repo = PermitRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [PermitRead.model_validate(p) for p in items]


@router.post("", response_model=PermitRead, status_code=status.HTTP_201_CREATED)
async def create_permit(payload: PermitCreate, db: AsyncSession = Depends(get_db)):
    repo = PermitRepository(db)
    permit = Permit(**payload.model_dump())
    created = await repo.create(permit)
    return PermitRead.model_validate(created)


@router.get("/expired", response_model=list[PermitRead])
async def expired(db: AsyncSession = Depends(get_db)):
    repo = PermitRepository(db)
    items = await repo.expired()
    return [PermitRead.model_validate(p) for p in items]


@router.get("/expiring", response_model=list[PermitRead])
async def expiring(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    repo = PermitRepository(db)
    items = await repo.expiring_within(days)
    return [PermitRead.model_validate(p) for p in items]


@router.get("/compliance-summary", response_model=ComplianceSummary)
async def summary(db: AsyncSession = Depends(get_db)):
    return await compliance_summary(db)


@router.patch("/{permit_id}", response_model=PermitRead)
async def update_permit(
    permit_id: uuid.UUID,
    payload: PermitUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = PermitRepository(db)
    permit = await repo.get_by_id(permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    updated = await repo.update(permit, payload.model_dump(exclude_unset=True))
    return PermitRead.model_validate(updated)


@router.delete("/{permit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permit(permit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PermitRepository(db)
    permit = await repo.get_by_id(permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    await repo.delete(permit)
