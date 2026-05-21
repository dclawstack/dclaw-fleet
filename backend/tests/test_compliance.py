from datetime import date, datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
async def test_hos_status_calculates_remaining_drive(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-HOS-1", "license_plate": "HOS-1", "make": "Ford", "model": "Transit", "year": 2024},
    )
    drv = await client.post(
        "/api/v1/drivers",
        json={"name": "Hour Slim", "email": "slim@example.com", "license_number": "DL-HOS-1"},
    )
    vid, did = veh.json()["id"], drv.json()["id"]

    base = datetime.now(timezone.utc).replace(hour=4, minute=0, second=0, microsecond=0)
    drive_start = base
    drive_end = base + timedelta(hours=5)
    await client.post(
        "/api/v1/hos-logs",
        json={
            "driver_id": did,
            "vehicle_id": vid,
            "duty_status": "driving",
            "started_at": drive_start.isoformat(),
            "ended_at": drive_end.isoformat(),
            "miles": 250,
        },
    )

    status = await client.get(f"/api/v1/hos-logs/drivers/{did}/status")
    assert status.status_code == 200
    body = status.json()
    assert body["driving_hours_today"] >= 4.9
    assert body["remaining_drive_hours"] <= 11 - 4.9


@pytest.mark.asyncio
async def test_permit_expiry_and_summary(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-PRM-1", "license_plate": "PR-1", "make": "Ford", "model": "Transit", "year": 2024},
    )
    vid = veh.json()["id"]

    expired = await client.post(
        "/api/v1/permits",
        json={
            "entity_type": "vehicle",
            "entity_id": vid,
            "permit_type": "DOT",
            "permit_number": "DOT-1",
            "expiry_date": (date.today() - timedelta(days=5)).isoformat(),
        },
    )
    assert expired.status_code == 201

    soon = await client.post(
        "/api/v1/permits",
        json={
            "entity_type": "vehicle",
            "entity_id": vid,
            "permit_type": "IFTA",
            "permit_number": "IFTA-1",
            "expiry_date": (date.today() + timedelta(days=10)).isoformat(),
        },
    )
    assert soon.status_code == 201

    exp = await client.get("/api/v1/permits/expired")
    assert len(exp.json()) == 1

    soon_list = await client.get("/api/v1/permits/expiring")
    assert len(soon_list.json()) == 1

    summary = await client.get("/api/v1/permits/compliance-summary")
    body = summary.json()
    assert body["expired_permits"] == 1
    assert body["expiring_soon"] == 1


@pytest.mark.asyncio
async def test_dvir_report(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-DVIR-1", "license_plate": "DV-1", "make": "Ford", "model": "F150", "year": 2024},
    )
    drv = await client.post(
        "/api/v1/drivers",
        json={"name": "Inspector Bob", "email": "bob@example.com", "license_number": "DL-INS-1"},
    )
    vid, did = veh.json()["id"], drv.json()["id"]

    resp = await client.post(
        "/api/v1/dvir",
        json={
            "driver_id": did,
            "vehicle_id": vid,
            "inspection_type": "pre_trip",
            "defects_count": 2,
            "passed": False,
            "notes": "Brake light out",
        },
    )
    assert resp.status_code == 201

    listing = await client.get(f"/api/v1/dvir/vehicles/{vid}")
    assert len(listing.json()) == 1
    assert listing.json()[0]["passed"] is False
