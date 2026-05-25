import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def enable_demo():
    """Most tests in this file run with demo mode on."""
    settings.enable_demo_mode = True
    yield
    settings.enable_demo_mode = False


@pytest.mark.asyncio
async def test_status_when_unseeded(anon_client):
    r = await anon_client.get("/api/v1/demo/status")
    assert r.status_code == 200
    body = r.json()
    assert body["enabled"] is True
    assert body["seeded"] is False
    assert body["vehicle_count"] == 0


@pytest.mark.asyncio
async def test_seed_creates_demo_dataset_and_user(anon_client):
    r = await anon_client.post("/api/v1/demo/seed")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"]["seeded"] is True
    assert body["status"]["vehicle_count"] == 5
    assert body["status"]["driver_count"] == 3
    assert body["credentials"]["email"] == "demo@dclaw.io"

    # Login as the demo user works
    login = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": body["credentials"]["email"], "password": body["credentials"]["password"]},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_seed_is_idempotent(anon_client):
    await anon_client.post("/api/v1/demo/seed")
    r = await anon_client.post("/api/v1/demo/seed")
    assert r.json()["status"]["vehicle_count"] == 5  # not 10


@pytest.mark.asyncio
async def test_reset_only_deletes_demo_records(anon_client, client):
    # Real (non-demo) data seeded via the authed client.
    real_vehicle = await client.post(
        "/api/v1/vehicles",
        json={"vin": "REAL-VIN-1", "license_plate": "REAL-1", "make": "Ford", "model": "F-150", "year": 2024},
    )
    assert real_vehicle.status_code == 201
    real_id = real_vehicle.json()["id"]

    # Seed + reset
    await anon_client.post("/api/v1/demo/seed")
    r = await anon_client.delete("/api/v1/demo/reset")
    assert r.status_code == 200
    body = r.json()
    assert body["vehicle_count"] == 0
    assert body["driver_count"] == 0

    # Real vehicle survives
    check = await client.get(f"/api/v1/vehicles/{real_id}")
    assert check.status_code == 200
    assert check.json()["license_plate"] == "REAL-1"


@pytest.mark.asyncio
async def test_flag_off_returns_disabled_status(anon_client):
    settings.enable_demo_mode = False
    r = await anon_client.get("/api/v1/demo/status")
    assert r.status_code == 200
    assert r.json()["enabled"] is False


@pytest.mark.asyncio
async def test_flag_off_blocks_seed_and_reset(anon_client):
    settings.enable_demo_mode = False
    r = await anon_client.post("/api/v1/demo/seed")
    assert r.status_code == 403
    r = await anon_client.delete("/api/v1/demo/reset")
    assert r.status_code == 403
