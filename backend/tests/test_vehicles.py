import pytest


def _payload(**overrides):
    base = {
        "vin": "1HGCM82633A123456",
        "license_plate": "ABC-123",
        "make": "Ford",
        "model": "Transit",
        "year": 2024,
        "fuel_type": "diesel",
        "odometer_miles": 12000,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_create_and_list_vehicle(client):
    resp = await client.post("/api/v1/vehicles", json=_payload())
    assert resp.status_code == 201, resp.text
    vid = resp.json()["id"]

    listing = await client.get("/api/v1/vehicles")
    assert listing.status_code == 200
    body = listing.json()
    assert body["meta"]["total"] == 1
    assert body["items"][0]["id"] == vid


@pytest.mark.asyncio
async def test_update_and_delete_vehicle(client):
    create = await client.post("/api/v1/vehicles", json=_payload())
    vid = create.json()["id"]

    patch = await client.patch(f"/api/v1/vehicles/{vid}", json={"status": "in_shop"})
    assert patch.status_code == 200
    assert patch.json()["status"] == "in_shop"

    delete = await client.delete(f"/api/v1/vehicles/{vid}")
    assert delete.status_code == 204

    not_found = await client.get(f"/api/v1/vehicles/{vid}")
    assert not_found.status_code == 404
