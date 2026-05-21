import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.dvir import DVIRReport
from app.repositories.dvir_repo import DVIRRepository
from app.schemas.dvir import DVIRReportCreate, DVIRReportRead

router = APIRouter()


@router.post("", response_model=DVIRReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(payload: DVIRReportCreate, db: AsyncSession = Depends(get_db)):
    repo = DVIRRepository(db)
    report = DVIRReport(**payload.model_dump())
    created = await repo.create(report)
    return DVIRReportRead.model_validate(created)


@router.get("", response_model=list[DVIRReportRead])
async def list_reports(db: AsyncSession = Depends(get_db)):
    repo = DVIRRepository(db)
    items, _ = await repo.list_all(limit=200)
    return [DVIRReportRead.model_validate(r) for r in items]


@router.get("/vehicles/{vehicle_id}", response_model=list[DVIRReportRead])
async def for_vehicle(vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DVIRRepository(db)
    items = await repo.for_vehicle(vehicle_id)
    return [DVIRReportRead.model_validate(r) for r in items]
