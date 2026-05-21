"""Carbon emission tracking — derives CO2 from existing fuel logs.

EPA factors:
- gasoline: 8.887 kg CO2 / US gallon
- diesel: 10.180 kg CO2 / US gallon
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.fuel_repo import FuelRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.predictive import CarbonReport

CO2_KG_PER_GAL = {
    "gasoline": 8.887,
    "diesel": 10.180,
    "electric": 0.0,
    "hybrid": 5.500,  # average effective
}


async def carbon_for_vehicle(db: AsyncSession, vehicle_id: uuid.UUID) -> CarbonReport:
    f_repo = FuelRepository(db)
    v_repo = VehicleRepository(db)
    vehicle = await v_repo.get_by_id(vehicle_id)
    logs = await f_repo.for_vehicle(vehicle_id)

    fuel_type = (vehicle.fuel_type if vehicle else "gasoline") or "gasoline"
    factor = CO2_KG_PER_GAL.get(fuel_type, CO2_KG_PER_GAL["gasoline"])

    gallons = sum(float(l.gallons) for l in logs)
    co2 = gallons * factor
    sorted_logs = sorted(logs, key=lambda l: l.odometer_miles)
    miles = sorted_logs[-1].odometer_miles - sorted_logs[0].odometer_miles if len(sorted_logs) >= 2 else 0
    miles = max(0, miles)
    per_mile_g = (co2 * 1000 / miles) if miles > 0 else 0

    suggestions: list[str] = []
    if fuel_type == "diesel":
        suggestions.append("Consider biodiesel B20 blend to cut net CO2 ~15%")
    if per_mile_g > 500 and fuel_type != "electric":
        suggestions.append("High emissions per mile — review driver behavior and tire pressure")
    if fuel_type in {"gasoline", "diesel"}:
        suggestions.append("Eco-routing through DClaw Route can shorten distance ~3-7%")

    return CarbonReport(
        vehicle_id=vehicle_id,
        co2_kg=round(co2, 2),
        fuel_gallons=round(gallons, 2),
        miles=miles,
        co2_per_mile_g=round(per_mile_g, 1),
        suggestions=suggestions,
    )


async def fleet_carbon(db: AsyncSession) -> CarbonReport:
    v_repo = VehicleRepository(db)
    vehicles, _ = await v_repo.list_all(limit=10_000)
    total_co2 = 0.0
    total_gal = 0.0
    total_miles = 0
    for v in vehicles:
        report = await carbon_for_vehicle(db, v.id)
        total_co2 += report.co2_kg
        total_gal += report.fuel_gallons
        total_miles += report.miles
    per_mile = (total_co2 * 1000 / total_miles) if total_miles > 0 else 0
    suggestions: list[str] = []
    if total_co2 > 0:
        suggestions.append(f"Annualized fleet footprint estimate: {total_co2 * 12:,.0f} kg CO2")
    if per_mile > 400:
        suggestions.append("Adopt eco-routing or EV transition for top-3 emitters")
    return CarbonReport(
        vehicle_id=None,
        co2_kg=round(total_co2, 2),
        fuel_gallons=round(total_gal, 2),
        miles=total_miles,
        co2_per_mile_g=round(per_mile, 1),
        suggestions=suggestions,
    )
