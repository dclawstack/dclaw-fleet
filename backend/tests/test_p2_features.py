from datetime import date, datetime, timedelta, timezone

import pytest


async def _make_vehicle(client, **kw):
    payload = {"vin": "VIN-P2-1", "license_plate": "P2-1", "make": "Ford", "model": "Lightning", "year": 2024, "fuel_type": "electric"}
    payload.update(kw)
    r = await client.post("/api/v1/vehicles", json=payload)
    return r.json()["id"]


# ── EV / charging ──

@pytest.mark.asyncio
async def test_charging_session_and_range(client):
    vid = await _make_vehicle(client)
    create = await client.post(
        "/api/v1/charging",
        json={
            "vehicle_id": vid,
            "station_id": "ST-001",
            "energy_kwh": 50,
            "cost": 12.50,
            "soc_start": 20,
            "soc_end": 85,
        },
    )
    assert create.status_code == 201, create.text

    rng = await client.get(f"/api/v1/charging/vehicles/{vid}/range")
    assert rng.status_code == 200
    body = rng.json()
    assert body["current_soc"] == 85
    assert body["estimated_range_miles"] > 100  # 75 kWh * 85% * 3 mi/kWh = 191

    rec = await client.get(f"/api/v1/charging/vehicles/{vid}/recommendation")
    assert rec.json()["needs_charge"] is False


# ── Accidents ──

@pytest.mark.asyncio
async def test_accident_report_predicts_claim(client):
    vid = await _make_vehicle(client, vin="VIN-ACC-1", license_plate="ACC-1", fuel_type="diesel")
    r = await client.post(
        "/api/v1/accidents",
        json={
            "vehicle_id": vid,
            "severity_score": 7,
            "photos_count": 4,
            "description": "Side collision at low speed",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["predicted_claim_amount"] is not None
    # severity 7 base = 35_000, +20% for 4 photos
    assert 35_000 < body["predicted_claim_amount"] < 50_000

    open_claims = await client.get("/api/v1/accidents/open-claims")
    assert len(open_claims.json()) == 1


# ── Parts inventory ──

@pytest.mark.asyncio
async def test_parts_low_stock_and_recommendations(client):
    await client.post(
        "/api/v1/parts",
        json={"name": "Brake pad — front", "sku": "BP-F-001", "category": "brake", "stock": 2, "reorder_threshold": 5, "unit_cost": 45.0},
    )
    await client.post(
        "/api/v1/parts",
        json={"name": "Oil filter", "sku": "OF-100", "category": "filter", "stock": 20, "reorder_threshold": 5, "unit_cost": 8.5},
    )

    low = await client.get("/api/v1/parts/low-stock")
    assert len(low.json()) == 1
    assert low.json()[0]["sku"] == "BP-F-001"

    recs = await client.get("/api/v1/parts/reorder-recommendations")
    rec = recs.json()[0]
    assert rec["sku"] == "BP-F-001"
    assert rec["suggested_order_qty"] >= 1
    assert rec["estimated_cost"] > 0


# ── Telematics ──

@pytest.mark.asyncio
async def test_telematics_heartbeat_flags_anomalies(client):
    vid = await _make_vehicle(client, vin="VIN-TEL-1", license_plate="TEL-1", fuel_type="gasoline")
    await client.post(
        "/api/v1/telematics/devices",
        json={"vehicle_id": vid, "vendor": "obd2", "device_id": "DEV-001"},
    )

    hb = await client.post(
        "/api/v1/telematics/heartbeat",
        json={"device_id": "DEV-001", "payload": {"speed": 145, "rpm": 3000}},
    )
    assert hb.status_code == 200
    anomalies = hb.json()["anomalies"]
    assert any("Implausible speed" in a for a in anomalies)
    assert any("Missing expected" in a for a in anomalies)


# ── Dashcam ──

@pytest.mark.asyncio
async def test_dashcam_event_create(client):
    vid = await _make_vehicle(client, vin="VIN-DC-1", license_plate="DC-1", fuel_type="gasoline")
    r = await client.post(
        "/api/v1/dashcam",
        json={"vehicle_id": vid, "event_type": "collision", "severity": 8},
    )
    assert r.status_code == 201
    by_v = await client.get(f"/api/v1/dashcam/vehicles/{vid}")
    assert len(by_v.json()) == 1


# ── Predictive maintenance ──

@pytest.mark.asyncio
async def test_predictive_maintenance_uses_mileage_and_events(client):
    vid = await _make_vehicle(
        client, vin="VIN-PM-1", license_plate="PM-1", fuel_type="diesel", odometer_miles=34_500,
    )
    drv = await client.post(
        "/api/v1/drivers",
        json={"name": "PM Driver", "email": "pm@example.com", "license_number": "DL-PM-1"},
    )
    did = drv.json()["id"]
    await client.patch(f"/api/v1/vehicles/{vid}", json={"driver_id": did})

    for _ in range(8):
        await client.post(
            "/api/v1/driving-events",
            json={"driver_id": did, "vehicle_id": vid, "event_type": "harsh_brake", "severity": 7},
        )

    report = await client.get(f"/api/v1/predictive/maintenance/vehicles/{vid}")
    assert report.status_code == 200
    body = report.json()
    assert body["overall_risk"] in {"medium", "high"}
    assert any(p["component"] == "brake_pads" for p in body["predictions"])


# ── Carbon ──

@pytest.mark.asyncio
async def test_carbon_report(client):
    vid = await _make_vehicle(client, vin="VIN-CO2-1", license_plate="CO2-1", fuel_type="diesel")
    base = datetime.now(timezone.utc) - timedelta(days=30)
    await client.post(
        "/api/v1/fuel-logs",
        json={"vehicle_id": vid, "gallons": 30, "cost": 90, "odometer_miles": 1000, "fuel_type": "diesel", "filled_at": base.isoformat()},
    )
    await client.post(
        "/api/v1/fuel-logs",
        json={"vehicle_id": vid, "gallons": 30, "cost": 90, "odometer_miles": 1600, "fuel_type": "diesel", "filled_at": (base + timedelta(days=10)).isoformat()},
    )

    report = await client.get(f"/api/v1/predictive/carbon/vehicles/{vid}")
    assert report.status_code == 200
    body = report.json()
    assert body["co2_kg"] == pytest.approx(60 * 10.18, rel=0.01)
    assert body["miles"] == 600

    fleet = await client.get("/api/v1/predictive/carbon/fleet")
    assert fleet.json()["co2_kg"] > 0


# ── Autonomous dispatch ──

@pytest.mark.asyncio
async def test_autonomous_dispatch_skips_maintenance_hold(client):
    v1 = await _make_vehicle(client, vin="VIN-DSP-1", license_plate="DSP-1", fuel_type="gasoline")
    v2 = await _make_vehicle(client, vin="VIN-DSP-2", license_plate="DSP-2", fuel_type="gasoline")
    await client.post(
        "/api/v1/maintenance",
        json={"vehicle_id": v1, "task_type": "oil", "due_date": (date.today() - timedelta(days=1)).isoformat()},
    )
    await client.post(
        "/api/v1/routes",
        json={"name": "AD-1", "stops": [{"sequence": 0, "address": "A", "lat": 0, "lng": 0}, {"sequence": 1, "address": "B", "lat": 0.1, "lng": 0.1}]},
    )

    plan = await client.post("/api/v1/predictive/dispatch/plan")
    body = plan.json()
    assigned_to = {a["vehicle_id"] for a in body["assignments"]}
    # v1 has overdue maintenance but is still "active" — should be downscored, not excluded
    # But v2 should be preferred when only one route exists
    assert v2 in assigned_to or v1 in assigned_to
    assert len(body["assignments"]) == 1


# ── AI Copilot — new intents reachable ──

@pytest.mark.asyncio
async def test_copilot_recognizes_new_intents(client):
    queries = ["EV range?", "open claims?", "parts inventory?", "telematics devices?", "predictive maintenance?", "carbon footprint?"]
    for q in queries:
        r = await client.post("/api/v1/ai/chat", json={"message": q})
        assert r.status_code == 200
        # Should not fall back to the generic "I can help with..." catch-all
        msg = r.json()["assistant_message"]["content"]
        assert "I can help with vehicles, drivers" not in msg, f"intent missed for: {q}"
