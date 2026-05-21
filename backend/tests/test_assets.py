import pytest


@pytest.mark.asyncio
async def test_asset_crud(client):
    create = await client.post(
        "/api/v1/assets",
        json={
            "name": "Pallet Jack 12",
            "asset_type": "equipment",
            "serial_number": "PJ-12-2024",
            "location": "Warehouse A",
        },
    )
    assert create.status_code == 201, create.text
    aid = create.json()["id"]

    patched = await client.patch(f"/api/v1/assets/{aid}", json={"status": "in_use"})
    assert patched.json()["status"] == "in_use"

    deleted = await client.delete(f"/api/v1/assets/{aid}")
    assert deleted.status_code == 204
