"""Predictive maintenance — heuristic failure prediction from existing telemetry.

Combines:
- vehicle.odometer_miles vs OEM service intervals
- driving_events count (harsh braking → brake wear, harsh acceleration → engine)
- dashcam events (collisions degrade alignment)
"""
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashcam_repo import DashcamRepository
from app.repositories.driving_event_repo import DrivingEventRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.predictive import PartFailurePrediction, PredictiveReport

LOOKBACK_DAYS = 60

COMPONENT_RULES = {
    "brake_pads": {"trigger_event": "harsh_brake", "miles_interval": 35_000, "miles_warn": 30_000},
    "transmission": {"trigger_event": "harsh_accel", "miles_interval": 100_000, "miles_warn": 90_000},
    "tires": {"trigger_event": "harsh_turn", "miles_interval": 50_000, "miles_warn": 45_000},
}


async def predict(db: AsyncSession, vehicle_id: uuid.UUID) -> PredictiveReport:
    vrepo = VehicleRepository(db)
    vehicle = await vrepo.get_by_id(vehicle_id)
    if vehicle is None:
        return PredictiveReport(vehicle_id=vehicle_id, overall_risk="low", predictions=[])

    de_repo = DrivingEventRepository(db)
    dc_repo = DashcamRepository(db)
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    events = await de_repo.for_driver(vehicle.driver_id, since=since) if vehicle.driver_id else []
    dc_events = await dc_repo.for_vehicle(vehicle_id)

    counts = Counter(e.event_type for e in events)
    miles = vehicle.odometer_miles

    predictions: list[PartFailurePrediction] = []
    for component, rule in COMPONENT_RULES.items():
        triggers = counts.get(rule["trigger_event"], 0)
        miles_part = miles % rule["miles_interval"]
        miles_factor = 0.0
        if miles_part >= rule["miles_warn"]:
            miles_factor = (miles_part - rule["miles_warn"]) / (rule["miles_interval"] - rule["miles_warn"])
        trigger_factor = min(triggers / 20.0, 1.0)  # 20 events → 1.0
        probability = round(min(1.0, miles_factor * 0.6 + trigger_factor * 0.4), 2)
        if probability < 0.2:
            continue
        action = "Inspect at next PM" if probability < 0.5 else "Schedule replacement now"
        reason = (
            f"odometer {miles_part:,}/{rule['miles_interval']:,} mi into service interval; "
            f"{triggers} {rule['trigger_event']} events in last {LOOKBACK_DAYS}d"
        )
        predictions.append(
            PartFailurePrediction(
                vehicle_id=vehicle_id,
                component=component,
                probability=probability,
                suggested_action=action,
                reason=reason,
            )
        )

    if any(e.event_type == "collision" for e in dc_events):
        predictions.append(
            PartFailurePrediction(
                vehicle_id=vehicle_id,
                component="alignment",
                probability=0.8,
                suggested_action="Schedule alignment check after collision event",
                reason="Dashcam collision event on record",
            )
        )

    if not predictions:
        overall = "low"
    else:
        top = max(p.probability for p in predictions)
        overall = "high" if top >= 0.7 else "medium" if top >= 0.4 else "low"

    return PredictiveReport(vehicle_id=vehicle_id, overall_risk=overall, predictions=predictions)
