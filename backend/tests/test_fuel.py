from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
async def test_fuel_logs_and_report(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={
            "vin": "VIN-FUEL-1",
            "license_plate": "FL-1",
            "make": "Chevy",
            "model": "Silverado",
            "year": 2022,
        },
    )
    vid = veh.json()["id"]

    base = datetime.now(timezone.utc) - timedelta(days=30)
    await client.post(
        "/api/v1/fuel-logs",
        json={
            "vehicle_id": vid,
            "gallons": 20,
            "cost": 60,
            "odometer_miles": 1000,
            "filled_at": base.isoformat(),
        },
    )
    await client.post(
        "/api/v1/fuel-logs",
        json={
            "vehicle_id": vid,
            "gallons": 20,
            "cost": 60,
            "odometer_miles": 1300,
            "filled_at": (base + timedelta(days=10)).isoformat(),
        },
    )
    await client.post(
        "/api/v1/fuel-logs",
        json={
            "vehicle_id": vid,
            "gallons": 20,
            "cost": 200,  # >50% over average — should flag fraud
            "odometer_miles": 1600,
            "filled_at": (base + timedelta(days=20)).isoformat(),
        },
    )

    report = await client.get(f"/api/v1/fuel-logs/vehicles/{vid}/report")
    assert report.status_code == 200
    body = report.json()
    assert body["total_miles"] == 600
    assert body["mpg"] is not None
    assert any("fraud" in a.lower() for a in body["anomalies"])
