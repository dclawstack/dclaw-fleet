import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.accident import AccidentReport
from app.repositories.accident_repo import AccidentRepository
from app.schemas.accident import (
    AccidentReportCreate,
    AccidentReportRead,
    AccidentReportUpdate,
)
from app.services.accident import predict_claim_amount

router = APIRouter()


@router.get("", response_model=list[AccidentReportRead])
async def list_reports(db: AsyncSession = Depends(get_db)):
    repo = AccidentRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [AccidentReportRead.model_validate(r) for r in items]


@router.post("", response_model=AccidentReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(payload: AccidentReportCreate, db: AsyncSession = Depends(get_db)):
    repo = AccidentRepository(db)
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = datetime.now(timezone.utc)
    report = AccidentReport(**data)
    report.predicted_claim_amount = predict_claim_amount(report)
    created = await repo.create(report)
    return AccidentReportRead.model_validate(created)


@router.get("/open-claims", response_model=list[AccidentReportRead])
async def open_claims(db: AsyncSession = Depends(get_db)):
    repo = AccidentRepository(db)
    items = await repo.open_claims()
    return [AccidentReportRead.model_validate(r) for r in items]


@router.get("/vehicles/{vehicle_id}", response_model=list[AccidentReportRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AccidentRepository(db)
    items = await repo.for_vehicle(vehicle_id)
    return [AccidentReportRead.model_validate(r) for r in items]


@router.patch("/{accident_id}", response_model=AccidentReportRead)
async def update_report(
    accident_id: uuid.UUID,
    payload: AccidentReportUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = AccidentRepository(db)
    report = await repo.get_by_id(accident_id)
    if not report:
        raise HTTPException(status_code=404, detail="Accident not found")
    updated = await repo.update(report, payload.model_dump(exclude_unset=True))
    updated.predicted_claim_amount = predict_claim_amount(updated)
    await db.commit()
    await db.refresh(updated)
    return AccidentReportRead.model_validate(updated)
