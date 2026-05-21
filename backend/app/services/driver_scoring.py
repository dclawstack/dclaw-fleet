"""Driver behavior scoring + coaching tips.

Score starts at 100 and decreases by severity per event over the lookback window.
"""
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driving_event import DrivingEvent
from app.repositories.driving_event_repo import DrivingEventRepository
from app.repositories.driver_repo import DriverRepository
from app.schemas.driving_event import CoachingTip, DriverCoaching, DriverScore

LOOKBACK_DAYS = 30

COACHING_TEMPLATES: dict[str, tuple[str, str]] = {
    # event_type → (severity_level, message)
    "harsh_brake": (
        "warning",
        "Frequent harsh braking detected. Increase following distance and look further ahead.",
    ),
    "harsh_accel": (
        "warning",
        "Aggressive acceleration drains fuel and tires. Try smoother throttle inputs.",
    ),
    "speeding": (
        "critical",
        "Speeding events recorded. Each 10 mph over 50 cuts fuel economy ~10%.",
    ),
    "idle": (
        "info",
        "Excessive idle time. Idling >5 min wastes ~0.5 gal/hr and adds emissions.",
    ),
    "harsh_turn": (
        "warning",
        "Sharp cornering events. Reduce speed approaching turns to improve safety and tire wear.",
    ),
}


def _compute_score(events: list[DrivingEvent]) -> int:
    score = 100
    for e in events:
        score -= e.severity
    return max(0, score)


async def score_driver(db: AsyncSession, driver_id: uuid.UUID) -> DriverScore:
    repo = DrivingEventRepository(db)
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    events = await repo.for_driver(driver_id, since=since)
    counter: Counter[str] = Counter(e.event_type for e in events)
    return DriverScore(
        driver_id=driver_id,
        score=_compute_score(events),
        event_count=len(events),
        events_by_type=dict(counter),
    )


async def coaching_tips(db: AsyncSession, driver_id: uuid.UUID) -> DriverCoaching:
    score = await score_driver(db, driver_id)
    tips: list[CoachingTip] = []
    for event_type, count in score.events_by_type.items():
        template = COACHING_TEMPLATES.get(event_type)
        if not template or count == 0:
            continue
        severity, base_msg = template
        tips.append(
            CoachingTip(
                event_type=event_type,
                severity=severity,
                message=f"{base_msg} (observed {count}× in last {LOOKBACK_DAYS}d)",
            )
        )
    return DriverCoaching(driver_id=driver_id, score=score.score, tips=tips)


async def persist_driver_safety_score(db: AsyncSession, driver_id: uuid.UUID) -> int:
    """Recompute score and write it back to Driver.safety_score."""
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        return 0
    score = await score_driver(db, driver_id)
    await repo.update(driver, {"safety_score": score.score})
    return score.score
