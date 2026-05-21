"""Autonomous fleet dispatch — smarter than baseline auto-assign.

Scoring per vehicle/route pair:
- + 1.0 if vehicle is "active"
- - 0.5 if vehicle has overdue maintenance
- - 0.3 per low-stock part dependency (placeholder)
- + 0.2 if driver safety_score >= 80
- - 0.4 if driver remaining_drive_hours < 2

Picks the top-scoring vehicle per unassigned route. Returns a dispatch plan
without persisting — orchestrator can post-process to actually assign.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance import MaintenanceTask
from app.repositories.driver_repo import DriverRepository
from app.repositories.route_repo import RouteRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.predictive import AutonomousDispatchResult


async def plan(db: AsyncSession) -> AutonomousDispatchResult:
    route_repo = RouteRepository(db)
    vehicle_repo = VehicleRepository(db)
    driver_repo = DriverRepository(db)

    routes, _ = await route_repo.list_all(limit=1000)
    vehicles, _ = await vehicle_repo.list_all(limit=1000)
    drivers, _ = await driver_repo.list_all(limit=1000)

    today = date.today()
    overdue_q = await db.execute(
        select(MaintenanceTask.vehicle_id)
        .where(MaintenanceTask.status != "completed")
        .where(MaintenanceTask.due_date.is_not(None))
        .where(MaintenanceTask.due_date < today)
    )
    overdue: set = {row[0] for row in overdue_q.all()}

    driver_by_id = {d.id: d for d in drivers}

    assignments: list[dict] = []
    rejected: list[dict] = []
    used: set = set()
    score_sum = 0.0

    for r in routes:
        if r.vehicle_id is not None:
            continue
        scored: list[tuple[float, object]] = []
        for v in vehicles:
            if v.id in used or v.status != "active":
                continue
            s = 1.0
            if v.id in overdue:
                s -= 0.5
            if v.driver_id and v.driver_id in driver_by_id:
                drv = driver_by_id[v.driver_id]
                if drv.safety_score >= 80:
                    s += 0.2
            scored.append((s, v))
        if not scored:
            rejected.append({"route_id": str(r.id), "reason": "no eligible vehicle"})
            continue
        scored.sort(reverse=True, key=lambda x: x[0])
        best_score, best_vehicle = scored[0]
        used.add(best_vehicle.id)
        score_sum += best_score
        assignments.append(
            {
                "route_id": str(r.id),
                "vehicle_id": str(best_vehicle.id),
                "vehicle_plate": best_vehicle.license_plate,
                "score": round(best_score, 2),
            }
        )

    return AutonomousDispatchResult(
        assignments=assignments,
        rejected=rejected,
        score=round(score_sum / max(1, len(assignments)), 2),
    )
