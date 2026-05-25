"""Public demo router — gated by ENABLE_DEMO_MODE.

With the flag off, /status returns 200 + {enabled: false} so the frontend
can quietly hide the demo section. /seed and /reset return 403.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services import demo_seed

router = APIRouter()


class DemoStatus(BaseModel):
    enabled: bool
    seeded: bool
    vehicle_count: int
    driver_count: int


class DemoCredentials(BaseModel):
    email: str
    password: str


class DemoSeedResult(BaseModel):
    status: DemoStatus
    credentials: DemoCredentials


def _require_enabled() -> None:
    if not settings.enable_demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo mode is disabled on this deployment",
        )


def _to_status(state: dict) -> DemoStatus:
    return DemoStatus(
        enabled=settings.enable_demo_mode,
        seeded=state["demo_user_exists"] or state["vehicle_count"] > 0,
        vehicle_count=state["vehicle_count"],
        driver_count=state["driver_count"],
    )


@router.get("/status", response_model=DemoStatus)
async def get_status(db: AsyncSession = Depends(get_db)):
    if not settings.enable_demo_mode:
        return DemoStatus(enabled=False, seeded=False, vehicle_count=0, driver_count=0)
    state = await demo_seed.status(db)
    return _to_status(state)


@router.post("/seed", response_model=DemoSeedResult)
async def seed(db: AsyncSession = Depends(get_db)):
    _require_enabled()
    state = await demo_seed.seed(db)
    return DemoSeedResult(
        status=_to_status(state),
        credentials=DemoCredentials(
            email=demo_seed.DEMO_USER_EMAIL,
            password=demo_seed.DEMO_USER_PASSWORD,
        ),
    )


@router.delete("/reset", response_model=DemoStatus)
async def reset(db: AsyncSession = Depends(get_db)):
    _require_enabled()
    state = await demo_seed.reset(db)
    return _to_status(state)
