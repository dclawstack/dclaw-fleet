import pytest

from tests.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD


@pytest.mark.asyncio
async def test_login_returns_jwt(anon_client):
    r = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
    assert body["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(anon_client):
    r = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_profile(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == TEST_ADMIN_EMAIL
    assert body["role"] == "admin"


@pytest.mark.asyncio
async def test_protected_route_blocks_anon(anon_client):
    r = await anon_client.get("/api/v1/vehicles")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_blocks_bad_token(anon_client):
    r = await anon_client.get(
        "/api/v1/vehicles",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_register_requires_admin(anon_client):
    """Without a token, /register should 401 — not 403, because the bearer dep fires first."""
    r = await anon_client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "pw", "name": "New", "role": "member"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_register_succeeds_with_admin_token(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "pw", "name": "New User", "role": "member"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "new@example.com"
    assert body["role"] == "member"


@pytest.mark.asyncio
async def test_register_rejects_member_token(client, anon_client):
    """A member-role token must not be able to register a new user."""
    # First, admin creates a member user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "member@example.com", "password": "pw", "name": "Mem", "role": "member"},
    )
    # Member logs in
    login = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "member@example.com", "password": "pw"},
    )
    member_token = login.json()["access_token"]
    # Member tries to register someone — should 403
    r = await anon_client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {member_token}"},
        json={"email": "other@example.com", "password": "pw", "name": "Other", "role": "member"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_health_remains_public(anon_client):
    r = await anon_client.get("/health/")
    assert r.status_code == 200
