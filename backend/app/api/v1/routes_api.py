import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.route import Route, RouteStop
from app.repositories.route_repo import RouteRepository
from app.schemas.common import Page, PageMeta
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.services.route_optimizer import optimize_route

router = APIRouter()


@router.get("", response_model=Page[RouteRead])
async def list_routes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = RouteRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return Page[RouteRead](
        items=[RouteRead.model_validate(r) for r in items],
        meta=PageMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
async def create_route(payload: RouteCreate, db: AsyncSession = Depends(get_db)):
    route = Route(
        name=payload.name,
        status=payload.status,
        vehicle_id=payload.vehicle_id,
    )
    db.add(route)
    await db.flush()
    for stop in payload.stops:
        db.add(RouteStop(route_id=route.id, **stop.model_dump()))
    await db.commit()
    await db.refresh(route)
    return RouteRead.model_validate(route)


@router.get("/{route_id}", response_model=RouteRead)
async def get_route(route_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return RouteRead.model_validate(route)


@router.patch("/{route_id}", response_model=RouteRead)
async def update_route(
    route_id: uuid.UUID,
    payload: RouteUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    updated = await repo.update(route, payload.model_dump(exclude_unset=True))
    return RouteRead.model_validate(updated)


@router.post("/{route_id}/optimize", response_model=RouteRead)
async def optimize(route_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    optimized = await optimize_route(db, route)
    return RouteRead.model_validate(optimized)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    await repo.delete(route)
