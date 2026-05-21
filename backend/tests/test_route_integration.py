import pytest


@pytest.mark.asyncio
async def test_sync_stamps_external_id(client):
    create = await client.post(
        "/api/v1/routes",
        json={
            "name": "Sync me",
            "stops": [
                {"sequence": 0, "address": "A", "lat": 37.7, "lng": -122.4},
                {"sequence": 1, "address": "B", "lat": 37.8, "lng": -122.3},
            ],
        },
    )
    rid = create.json()["id"]
    await client.post(f"/api/v1/routes/{rid}/optimize")

    sync = await client.post("/api/v1/route-integration/sync")
    assert sync.status_code == 200
    body = sync.json()
    assert body["synced_count"] == 1


@pytest.mark.asyncio
async def test_auto_assign_skips_maintenance_hold(client):
    # Two active vehicles, one with overdue maintenance (should be skipped)
    v1 = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-RI-1", "license_plate": "RI-1", "make": "Ford", "model": "T", "year": 2024},
    )
    v2 = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-RI-2", "license_plate": "RI-2", "make": "Ford", "model": "T", "year": 2024},
    )
    v1_id, v2_id = v1.json()["id"], v2.json()["id"]

    from datetime import date, timedelta
    await client.post(
        "/api/v1/maintenance",
        json={
            "vehicle_id": v1_id,
            "task_type": "oil",
            "due_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )

    await client.post(
        "/api/v1/routes",
        json={
            "name": "R1",
            "stops": [
                {"sequence": 0, "address": "A", "lat": 0, "lng": 0},
                {"sequence": 1, "address": "B", "lat": 0.1, "lng": 0.1},
            ],
        },
    )
    await client.post(
        "/api/v1/routes",
        json={
            "name": "R2",
            "stops": [
                {"sequence": 0, "address": "C", "lat": 0, "lng": 0},
                {"sequence": 1, "address": "D", "lat": 0.1, "lng": 0.1},
            ],
        },
    )

    assign = await client.post("/api/v1/route-integration/auto-assign")
    body = assign.json()
    assert body["skipped_count"] == 1
    assigned_to = {a["vehicle_id"] for a in body["assignments"] if a["vehicle_id"]}
    assert v1_id not in assigned_to  # vehicle on hold not assigned
    assert v2_id in assigned_to
