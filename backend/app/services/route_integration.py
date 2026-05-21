"""DClaw Route integration — sync routes and auto-assign vehicles.

This is a STUB. The real implementation will call DClaw Route's HTTP API
to push optimized routes and pull driver assignments. Here we simulate the
sync locally so the rest of the platform can wire against a stable contract.
"""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance import MaintenanceTask
from app.models.route import Route
from app.models.vehicle import Vehicle
from app.repositories.route_repo import RouteRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.route_integration import (
    AutoAssignResult,
    RouteAssignment,
    RouteSyncResult,
)


async def sync_routes(db: AsyncSession) -> RouteSyncResult:
    """Pretend to push every optimized route to DClaw Route.

    Stamps `external_id` and `synced_at` on each route so the UI can show sync state.
    """
    repo = RouteRepository(db)
    routes, _ = await repo.list_all(limit=1000)
    now = datetime.now(timezone.utc)
    synced: list[uuid.UUID] = []
    failed = 0
    for r in routes:
        if r.status != "optimized":
            failed += 1
            continue
        r.external_id = r.external_id or f"DCR-{r.id.hex[:12]}"
        r.synced_at = now
        synced.append(r.id)
    await db.commit()
    return RouteSyncResult(
        synced_count=len(synced),
        failed_count=failed,
        synced_route_ids=synced,
        synced_at=now,
    )


async def auto_assign(db: AsyncSession) -> AutoAssignResult:
    """Assign unassigned routes to active vehicles.

    Skips vehicles that have overdue maintenance (maintenance hold).
    Round-robins across remaining vehicles, one route per vehicle per call.
    """
    route_repo = RouteRepository(db)
    vehicle_repo = VehicleRepository(db)

    routes_all, _ = await route_repo.list_all(limit=1000)
    unassigned = [r for r in routes_all if r.vehicle_id is None]

    vehicles_all, _ = await vehicle_repo.list_all(limit=1000)
    active_vehicles = [v for v in vehicles_all if v.status == "active"]

    today = date.today()
    on_hold_q = await db.execute(
        select(MaintenanceTask.vehicle_id)
        .where(MaintenanceTask.status != "completed")
        .where(MaintenanceTask.due_date.is_not(None))
        .where(MaintenanceTask.due_date < today)
    )
    on_hold: set[uuid.UUID] = {row[0] for row in on_hold_q.all()}

    available: list[Vehicle] = [v for v in active_vehicles if v.id not in on_hold]
    assignments: list[RouteAssignment] = []
    skipped_reasons: list[str] = []
    pool = list(available)

    for r in unassigned:
        if not pool:
            assignments.append(
                RouteAssignment(
                    route_id=r.id,
                    vehicle_id=None,
                    vehicle_plate=None,
                    reason="No available vehicle",
                )
            )
            continue
        v = pool.pop(0)
        r.vehicle_id = v.id
        assignments.append(
            RouteAssignment(
                route_id=r.id,
                vehicle_id=v.id,
                vehicle_plate=v.license_plate,
                reason="Assigned",
            )
        )

    skipped = len(on_hold)
    if skipped:
        skipped_reasons.append(f"{skipped} vehicle(s) on maintenance hold")

    await db.commit()
    return AutoAssignResult(
        assignments=assignments,
        skipped_count=skipped,
        skipped_reasons=skipped_reasons,
    )
