"""Compliance & ELD service — HOS clock, DVIR aggregation, permit expiry."""
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dvir_repo import DVIRRepository
from app.repositories.hos_repo import HOSRepository
from app.repositories.permit_repo import PermitRepository
from app.schemas.hos import HOSStatus
from app.schemas.permit import ComplianceSummary

# Federal limits (49 CFR §395.3) — simplified property-carrying driver rules
MAX_DRIVE_HOURS = 11.0
MAX_ON_DUTY_HOURS = 14.0
DRIVING_STATUSES = {"driving"}
ON_DUTY_STATUSES = {"driving", "on_duty"}


def _hours_between(start: datetime, end: datetime | None) -> float:
    end = end or datetime.now(timezone.utc)
    return max(0.0, (end - start).total_seconds() / 3600.0)


async def hos_status_for_driver(db: AsyncSession, driver_id: uuid.UUID) -> HOSStatus:
    repo = HOSRepository(db)
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    logs = await repo.for_driver(driver_id, since=midnight)
    current = await repo.current_for_driver(driver_id)
    current_status = current.duty_status if current else "off_duty"

    driving = 0.0
    on_duty = 0.0
    for log in logs:
        h = _hours_between(log.started_at, log.ended_at)
        if log.duty_status in DRIVING_STATUSES:
            driving += h
        if log.duty_status in ON_DUTY_STATUSES:
            on_duty += h

    violations: list[str] = []
    if driving > MAX_DRIVE_HOURS:
        violations.append(f"11-hour driving limit exceeded ({driving:.1f}h)")
    if on_duty > MAX_ON_DUTY_HOURS:
        violations.append(f"14-hour on-duty limit exceeded ({on_duty:.1f}h)")

    return HOSStatus(
        driver_id=driver_id,
        current_status=current_status,
        on_duty_hours_today=round(on_duty, 2),
        driving_hours_today=round(driving, 2),
        remaining_drive_hours=max(0.0, round(MAX_DRIVE_HOURS - driving, 2)),
        remaining_duty_hours=max(0.0, round(MAX_ON_DUTY_HOURS - on_duty, 2)),
        violations=violations,
    )


async def compliance_summary(db: AsyncSession) -> ComplianceSummary:
    permit_repo = PermitRepository(db)
    dvir_repo = DVIRRepository(db)
    today = date.today()
    expired = await permit_repo.expired(today)
    expiring = await permit_repo.expiring_within(30, today)
    failed_dvir = await dvir_repo.failed_since(datetime.now(timezone.utc) - timedelta(days=30))
    # HOS violations count — naive scan handled per-driver elsewhere; placeholder 0 here.
    return ComplianceSummary(
        expired_permits=len(expired),
        expiring_soon=len(expiring),
        failed_dvir=len(failed_dvir),
        hos_violations=0,
    )
