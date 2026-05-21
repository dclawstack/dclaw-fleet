from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.route_integration import AutoAssignResult, RouteSyncResult
from app.services.route_integration import auto_assign, sync_routes

router = APIRouter()


@router.post("/sync", response_model=RouteSyncResult)
async def sync(db: AsyncSession = Depends(get_db)):
    return await sync_routes(db)


@router.post("/auto-assign", response_model=AutoAssignResult)
async def auto_assign_endpoint(db: AsyncSession = Depends(get_db)):
    return await auto_assign(db)
