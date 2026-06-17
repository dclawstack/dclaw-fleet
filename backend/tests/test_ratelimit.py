import pytest

from app.core.cache import cache
from app.core.config import settings
from app.core.ratelimit import RateLimiter, limiter


@pytest.fixture
def rate_limit_on():
    """Enable rate limiting with small limits for a single test."""
    limiter.clear()
    settings.rate_limit_enabled = True
    original = (settings.rate_limit_per_minute, settings.auth_rate_limit_per_minute)
    settings.rate_limit_per_minute = 3
    settings.auth_rate_limit_per_minute = 2
    yield
    settings.rate_limit_enabled = False
    settings.rate_limit_per_minute, settings.auth_rate_limit_per_minute = original
    limiter.clear()


@pytest.mark.asyncio
async def test_global_limit_returns_429(client, rate_limit_on):
    for _ in range(3):
        ok = await client.get("/api/v1/vehicles")
        assert ok.status_code == 200

    blocked = await client.get("/api/v1/vehicles")
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"]
    assert blocked.headers["X-RateLimit-Limit"] == "3"
    assert blocked.headers["X-RateLimit-Remaining"] == "0"


@pytest.mark.asyncio
async def test_remaining_header_decrements(client, rate_limit_on):
    first = await client.get("/api/v1/vehicles")
    assert first.headers["X-RateLimit-Remaining"] == "2"


@pytest.mark.asyncio
async def test_auth_endpoints_have_stricter_limit(anon_client, rate_limit_on):
    creds = {"email": "nobody@example.com", "password": "wrong"}
    for _ in range(2):
        resp = await anon_client.post("/api/v1/auth/login", json=creds)
        assert resp.status_code == 401  # counted, but auth fails

    blocked = await anon_client.post("/api/v1/auth/login", json=creds)
    assert blocked.status_code == 429


@pytest.mark.asyncio
async def test_limiter_runs_before_cache(client, rate_limit_on):
    """Cached repeats must still count against the limit (limiter is outermost)."""
    cache.clear()
    settings.cache_enabled = True
    try:
        statuses = [
            (await client.get("/api/v1/vehicles")).status_code for _ in range(4)
        ]
    finally:
        settings.cache_enabled = False
        cache.clear()
    assert statuses == [200, 200, 200, 429]


def test_ratelimiter_fixed_window():
    rl = RateLimiter()
    assert rl.check("ip:global", 2) == (True, 1, 0)
    assert rl.check("ip:global", 2) == (True, 0, 0)
    allowed, remaining, retry_after = rl.check("ip:global", 2)
    assert allowed is False
    assert remaining == 0
    assert retry_after >= 1
