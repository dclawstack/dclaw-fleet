from datetime import date, timedelta

import pytest


@pytest.mark.asyncio
async def test_maintenance_task_flow(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={
            "vin": "VIN-MAINT-1",
            "license_plate": "MT-1",
            "make": "Ford",
            "model": "Transit",
            "year": 2023,
            "odometer_miles": 80_000,
        },
    )
    vid = veh.json()["id"]

    task = await client.post(
        "/api/v1/maintenance",
        json={
            "vehicle_id": vid,
            "task_type": "oil_change",
            "due_date": (date.today() - timedelta(days=2)).isoformat(),
            "due_mileage": 80_500,
        },
    )
    assert task.status_code == 201, task.text

    overdue = await client.get("/api/v1/maintenance/overdue")
    assert overdue.status_code == 200
    assert len(overdue.json()) == 1

    score = await client.get(f"/api/v1/maintenance/vehicles/{vid}/health-score")
    assert score.status_code == 200
    assert score.json()["health_score"] < 100

    auto = await client.post(f"/api/v1/maintenance/vehicles/{vid}/auto-schedule")
    assert auto.status_code == 200
    assert auto.json() is not None
    assert auto.json()["task_type"] == "preventive"

    again = await client.post(f"/api/v1/maintenance/vehicles/{vid}/auto-schedule")
    assert again.json() is None  # idempotent — already scheduled
