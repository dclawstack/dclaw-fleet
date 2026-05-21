from datetime import date

import pytest


@pytest.mark.asyncio
async def test_auto_categorize_and_approval(client):
    veh = await client.post(
        "/api/v1/vehicles",
        json={"vin": "VIN-EX-1", "license_plate": "EX-1", "make": "Ford", "model": "Transit", "year": 2024},
    )
    vid = veh.json()["id"]

    create = await client.post(
        "/api/v1/expenses",
        json={
            "vehicle_id": vid,
            "category": "other",
            "amount": 80.00,
            "vendor": "Shell Gas Station",
            "expense_date": date.today().isoformat(),
        },
    )
    assert create.status_code == 201
    expense = create.json()
    assert expense["category"] == "fuel"  # auto-categorized from "Shell"
    assert expense["approval_status"] == "pending"

    pending = await client.get("/api/v1/expenses/pending")
    assert len(pending.json()) == 1

    approval = await client.post(
        f"/api/v1/expenses/{expense['id']}/approve",
        json={"approved_by": "manager@fleet.io", "approve": True},
    )
    assert approval.status_code == 200
    assert approval.json()["approval_status"] == "approved"


@pytest.mark.asyncio
async def test_analytics_flags_oversize_and_duplicate(client):
    today = date.today().isoformat()
    await client.post(
        "/api/v1/expenses",
        json={"category": "maintenance", "amount": 5_000, "vendor": "Mega Shop", "expense_date": today},
    )
    await client.post(
        "/api/v1/expenses",
        json={"category": "lodging", "amount": 120, "vendor": "Marriott", "expense_date": today},
    )
    await client.post(
        "/api/v1/expenses",
        json={"category": "lodging", "amount": 120, "vendor": "Marriott", "expense_date": today},
    )

    analytics = await client.get("/api/v1/expenses/analytics")
    body = analytics.json()
    assert body["total_amount"] >= 5_240
    assert body["flagged_count"] >= 2
    flags_joined = " ".join(body["flags"])
    assert "Oversized" in flags_joined
    assert "duplicate" in flags_joined.lower()
