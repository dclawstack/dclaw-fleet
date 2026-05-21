import pytest


async def _make_vehicle_and_driver(client):
    v = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-DB-1", "license_plate": "DB-1", "make": "Ford", "model": "Transit", "year": 2024},
    )
    d = await client.post(
        "/api/v1/drivers",
        json={"name": "Sam Risky", "email": "sam@example.com", "license_number": "DL-7777"},
    )
    return v.json()["id"], d.json()["id"]


@pytest.mark.asyncio
async def test_score_and_coaching(client):
    vid, did = await _make_vehicle_and_driver(client)

    for et, sev in [("harsh_brake", 6), ("harsh_brake", 7), ("speeding", 9), ("idle", 2)]:
        r = await client.post(
            "/api/v1/driving-events",
            json={"driver_id": did, "vehicle_id": vid, "event_type": et, "severity": sev},
        )
        assert r.status_code == 201, r.text

    score = await client.get(f"/api/v1/driving-events/drivers/{did}/score")
    assert score.status_code == 200
    body = score.json()
    assert body["event_count"] == 4
    assert body["score"] == 100 - (6 + 7 + 9 + 2)
    assert body["events_by_type"]["harsh_brake"] == 2

    coaching = await client.get(f"/api/v1/driving-events/drivers/{did}/coaching")
    assert coaching.status_code == 200
    tips = coaching.json()["tips"]
    assert {t["event_type"] for t in tips} == {"harsh_brake", "speeding", "idle"}

    persisted = await client.post(f"/api/v1/driving-events/drivers/{did}/recompute-score")
    assert persisted.status_code == 200
    assert persisted.json()["safety_score"] == body["score"]
