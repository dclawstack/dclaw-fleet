from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance import MaintenanceTask
from app.models.vehicle import Vehicle
from app.repositories.maintenance_repo import MaintenanceRepository
from app.repositories.vehicle_repo import VehicleRepository

PM_INTERVAL_MILES = 5_000
PM_INTERVAL_DAYS = 90


async def auto_schedule_for_vehicle(
    db: AsyncSession,
    vehicle: Vehicle,
) -> MaintenanceTask | None:
    """Auto-schedule a preventive maintenance task if none is pending for this vehicle."""
    repo = MaintenanceRepository(db)
    existing = await repo.for_vehicle(vehicle.id)
    pending = [t for t in existing if t.status == "scheduled" and t.task_type == "preventive"]
    if pending:
        return None
    task = MaintenanceTask(
        vehicle_id=vehicle.id,
        task_type="preventive",
        description=f"Routine PM at {vehicle.odometer_miles + PM_INTERVAL_MILES} miles",
        due_date=date.today() + timedelta(days=PM_INTERVAL_DAYS),
        due_mileage=vehicle.odometer_miles + PM_INTERVAL_MILES,
        status="scheduled",
    )
    return await repo.create(task)


async def scan_overdue(db: AsyncSession) -> list[MaintenanceTask]:
    repo = MaintenanceRepository(db)
    return await repo.overdue(date.today())


async def vehicle_health_score(db: AsyncSession, vehicle: Vehicle) -> int:
    """Score 0–100 based on overdue + scheduled task count.

    Each overdue task costs 15 points, each scheduled-but-not-overdue costs 3.
    """
    repo = MaintenanceRepository(db)
    tasks = await repo.for_vehicle(vehicle.id)
    today = date.today()
    score = 100
    for t in tasks:
        if t.status == "completed":
            continue
        if t.due_date and t.due_date < today:
            score -= 15
        else:
            score -= 3
    repo2 = VehicleRepository(db)
    _ = repo2  # placeholder to keep import used; future-extend with vehicle-driven signals
    return max(0, score)
