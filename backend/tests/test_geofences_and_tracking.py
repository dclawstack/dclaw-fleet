import pytest

from app.services.tracking import evaluate_geofences, haversine_m


def test_haversine_known_distance():
    # ~111 km between (0,0) and (1,0)
    d = haversine_m(0, 0, 1, 0)
    assert 110_000 < d < 112_000


def test_evaluate_inclusion_breach():
    from uuid import uuid4

    from app.models.geofence import Geofence

    fence = Geofence(
        id=uuid4(),
        name="Depot",
        fence_type="inclusion",
        center_lat=0.0,
        center_lng=0.0,
        radius_m=1000,
    )
    alerts = evaluate_geofences(0.0, 0.05, uuid4(), [fence])  # ~5km away
    assert len(alerts) == 1
    assert alerts[0].breach_type == "exit"


def test_evaluate_exclusion_breach():
    from uuid import uuid4

    from app.models.geofence import Geofence

    fence = Geofence(
        id=uuid4(),
        name="Restricted",
        fence_type="exclusion",
        center_lat=0.0,
        center_lng=0.0,
        radius_m=10_000,
    )
    alerts = evaluate_geofences(0.0, 0.05, uuid4(), [fence])  # inside 5km
    assert len(alerts) == 1
    assert alerts[0].breach_type == "entry"


@pytest.mark.asyncio
async def test_geofence_crud(client):
    create = await client.post(
        "/api/v1/geofences",
        json={
            "name": "HQ",
            "fence_type": "inclusion",
            "center_lat": 37.7749,
            "center_lng": -122.4194,
            "radius_m": 500,
        },
    )
    assert create.status_code == 201, create.text
    assert create.json()["radius_m"] == 500


@pytest.mark.asyncio
async def test_ingest_ping_and_breach(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={
            "vin": "VIN-TRACK-1",
            "license_plate": "TRK-1",
            "make": "Ford",
            "model": "F150",
            "year": 2024,
        },
    )
    vid = veh.json()["id"]

    await client.post(
        "/api/v1/geofences",
        json={
            "name": "Depot",
            "fence_type": "inclusion",
            "center_lat": 0.0,
            "center_lng": 0.0,
            "radius_m": 1000,
        },
    )

    resp = await client.post(
        "/api/v1/locations/ingest",
        json={"vehicle_id": vid, "lat": 0.05, "lng": 0.0, "speed_mph": 35},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["ping"]["vehicle_id"] == vid
    assert len(body["breach_alerts"]) == 1
    assert body["breach_alerts"][0]["breach_type"] == "exit"

    latest = await client.get("/api/v1/locations/latest")
    assert latest.status_code == 200
    assert len(latest.json()) == 1
