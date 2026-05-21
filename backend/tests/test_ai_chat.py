import pytest


@pytest.mark.asyncio
async def test_chat_greeting_with_empty_fleet(client):
    resp = await client.post("/api/v1/ai/chat", json={"message": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["assistant_message"]["role"] == "assistant"
    assert "0 vehicles" in body["assistant_message"]["content"]
    assert len(body["suggested_actions"]) > 0


@pytest.mark.asyncio
async def test_chat_followup_preserves_session(client):
    first = await client.post("/api/v1/ai/chat", json={"message": "hi there"})
    sid = first.json()["session_id"]

    second = await client.post(
        "/api/v1/ai/chat",
        json={"session_id": sid, "message": "how many vehicles do I have?"},
    )
    assert second.status_code == 200
    assert second.json()["session_id"] == sid

    session = await client.get(f"/api/v1/ai/sessions/{sid}")
    assert session.status_code == 200
    assert len(session.json()["messages"]) == 4  # 2 user + 2 assistant


@pytest.mark.asyncio
async def test_chat_uses_live_data(client):
    await client.post(
        "/api/v1/vehicles",
        json={
            "vin": "VIN-CHAT-1",
            "license_plate": "AI-1",
            "make": "Tesla",
            "model": "Semi",
            "year": 2025,
        },
    )
    resp = await client.post("/api/v1/ai/chat", json={"message": "count my vehicles"})
    body = resp.json()
    assert "1 vehicles" in body["assistant_message"]["content"]
