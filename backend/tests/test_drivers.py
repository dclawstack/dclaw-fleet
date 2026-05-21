import pytest


@pytest.mark.asyncio
async def test_driver_crud(client):
    create = await client.post(
        "/api/v1/drivers",
        json={
            "name": "Alex Driver",
            "email": "alex@example.com",
            "license_number": "DL-9981",
            "safety_score": 92,
        },
    )
    assert create.status_code == 201, create.text
    did = create.json()["id"]

    fetched = await client.get(f"/api/v1/drivers/{did}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "alex@example.com"

    patched = await client.patch(f"/api/v1/drivers/{did}", json={"safety_score": 80})
    assert patched.json()["safety_score"] == 80

    listing = await client.get("/api/v1/drivers")
    assert listing.json()["meta"]["total"] == 1
