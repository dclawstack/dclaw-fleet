"""EV management — range prediction + charge-scheduling recommendation.

Stub heuristics: 3 mi/kWh efficiency, target SoC 80% by morning. Replace with
real ML model once telemetry stream exists.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.charging_repo import ChargingRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.charging import ChargeRecommendation, RangePrediction

EFFICIENCY_MI_PER_KWH = 3.0
TARGET_SOC = 80.0
CHARGE_THRESHOLD_SOC = 30.0
USABLE_BATTERY_KWH = 75.0  # representative midsize EV


async def predict_range(db: AsyncSession, vehicle_id: uuid.UUID) -> RangePrediction:
    repo = ChargingRepository(db)
    latest = await repo.latest_for_vehicle(vehicle_id)
    notes: list[str] = []

    if latest is None or latest.soc_end is None:
        return RangePrediction(
            vehicle_id=vehicle_id,
            current_soc=None,
            estimated_range_miles=0.0,
            confidence="low",
            notes=["No prior charging data — log a session to enable predictions"],
        )

    current_soc = latest.soc_end
    energy_remaining_kwh = USABLE_BATTERY_KWH * (current_soc / 100.0)
    estimated_range = energy_remaining_kwh * EFFICIENCY_MI_PER_KWH

    confidence = "high" if current_soc > 30 else "medium" if current_soc > 10 else "low"
    if current_soc < CHARGE_THRESHOLD_SOC:
        notes.append("State of charge below 30% — schedule charge before next dispatch")

    return RangePrediction(
        vehicle_id=vehicle_id,
        current_soc=current_soc,
        estimated_range_miles=round(estimated_range, 1),
        confidence=confidence,
        notes=notes,
    )


async def charge_recommendation(db: AsyncSession, vehicle_id: uuid.UUID) -> ChargeRecommendation:
    repo = ChargingRepository(db)
    latest = await repo.latest_for_vehicle(vehicle_id)
    current = (latest.soc_end if latest and latest.soc_end is not None else 100.0)
    needs = current < CHARGE_THRESHOLD_SOC
    return ChargeRecommendation(
        vehicle_id=vehicle_id,
        needs_charge=needs,
        target_soc=TARGET_SOC,
        suggested_window="22:00–06:00 (off-peak)",
        reason=(
            f"SoC {current:.0f}% below {CHARGE_THRESHOLD_SOC:.0f}% threshold"
            if needs
            else f"SoC {current:.0f}% sufficient for next shift"
        ),
    )


async def ensure_vehicle(db: AsyncSession, vehicle_id: uuid.UUID) -> bool:
    vrepo = VehicleRepository(db)
    return (await vrepo.get_by_id(vehicle_id)) is not None
