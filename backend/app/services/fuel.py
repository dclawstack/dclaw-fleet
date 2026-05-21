import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.fuel_repo import FuelRepository
from app.schemas.fuel import FuelEfficiencyReport


async def efficiency_report(
    db: AsyncSession, vehicle_id: uuid.UUID
) -> FuelEfficiencyReport:
    repo = FuelRepository(db)
    logs = await repo.for_vehicle(vehicle_id)
    if not logs:
        return FuelEfficiencyReport(
            vehicle_id=vehicle_id,
            total_gallons=0,
            total_cost=0,
            total_miles=0,
            mpg=None,
            anomalies=[],
        )

    sorted_logs = sorted(logs, key=lambda l: l.filled_at)
    total_gallons = sum(float(l.gallons) for l in sorted_logs)
    total_cost = sum(float(l.cost) for l in sorted_logs)
    miles = sorted_logs[-1].odometer_miles - sorted_logs[0].odometer_miles
    mpg = (miles / total_gallons) if total_gallons > 0 and miles > 0 else None

    anomalies: list[str] = []
    if mpg is not None and mpg < 8:
        anomalies.append(f"Low MPG ({mpg:.1f}) — investigate driver behavior or vehicle condition")

    costs_per_gallon = [float(l.cost) / float(l.gallons) for l in sorted_logs if l.gallons > 0]
    if costs_per_gallon:
        avg = sum(costs_per_gallon) / len(costs_per_gallon)
        for l, cpg in zip(sorted_logs, costs_per_gallon):
            if avg > 0 and cpg > avg * 1.5:
                anomalies.append(
                    f"Fuel-up on {l.filled_at.date()} priced 50%+ above average — possible fraud"
                )
                break

    for i in range(1, len(sorted_logs)):
        gap = sorted_logs[i].odometer_miles - sorted_logs[i - 1].odometer_miles
        if gap < 0:
            anomalies.append(f"Odometer rollback detected on {sorted_logs[i].filled_at.date()}")
            break

    return FuelEfficiencyReport(
        vehicle_id=vehicle_id,
        total_gallons=total_gallons,
        total_cost=total_cost,
        total_miles=max(0, miles),
        mpg=mpg,
        anomalies=anomalies,
    )
