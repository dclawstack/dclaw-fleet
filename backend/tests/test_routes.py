import pytest


@pytest.mark.asyncio
async def test_route_create_and_optimize(client):
    create = await client.post(
        "/api/v1/routes",
        json={
            "name": "Morning Loop",
            "stops": [
                {"sequence": 0, "address": "Stop A", "lat": 37.7749, "lng": -122.4194},
                {"sequence": 1, "address": "Stop B", "lat": 37.7849, "lng": -122.4094},
                {"sequence": 2, "address": "Stop C", "lat": 37.7949, "lng": -122.3994},
            ],
        },
    )
    assert create.status_code == 201, create.text
    rid = create.json()["id"]
    assert len(create.json()["stops"]) == 3

    optimized = await client.post(f"/api/v1/routes/{rid}/optimize")
    assert optimized.status_code == 200
    body = optimized.json()
    assert body["status"] == "optimized"
    assert body["optimized_distance_miles"] is not None
    assert body["optimized_duration_min"] is not None
