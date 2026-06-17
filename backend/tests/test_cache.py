import time

import pytest

from app.core.cache import TTLCache, _Entry, cache
from app.core.config import settings


def _vehicle(**overrides):
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


@pytest.fixture
def caching_on():
    """Enable the response cache for a single test and isolate its state."""
    cache.clear()
    settings.cache_enabled = True
    yield
    settings.cache_enabled = False
    cache.clear()


@pytest.mark.asyncio
async def test_get_is_cached_after_first_call(client, caching_on):
    first = await client.get("/api/v1/vehicles")
    assert first.status_code == 200
    assert first.headers["X-Cache"] == "MISS"

    second = await client.get("/api/v1/vehicles")
    assert second.status_code == 200
    assert second.headers["X-Cache"] == "HIT"
    assert second.json() == first.json()
    assert second.headers["ETag"] == first.headers["ETag"]


@pytest.mark.asyncio
async def test_if_none_match_returns_304(client, caching_on):
    resp = await client.get("/api/v1/vehicles")
    etag = resp.headers["ETag"]

    not_modified = await client.get(
        "/api/v1/vehicles", headers={"If-None-Match": etag}
    )
    assert not_modified.status_code == 304
    assert not_modified.content == b""


@pytest.mark.asyncio
async def test_write_invalidates_cached_list(client, caching_on):
    empty = await client.get("/api/v1/vehicles")
    assert empty.json()["meta"]["total"] == 0

    create = await client.post("/api/v1/vehicles", json=_vehicle())
    assert create.status_code == 201

    refreshed = await client.get("/api/v1/vehicles")
    assert refreshed.headers["X-Cache"] == "MISS"
    assert refreshed.json()["meta"]["total"] == 1


def test_ttlcache_expires_entries():
    store = TTLCache()
    store.set("k", _Entry(b"body", "application/json", '"e"', time.monotonic() - 1))
    assert store.get("k") is None


def test_ttlcache_is_bounded_by_max_entries():
    store = TTLCache(max_entries=2)
    future = time.monotonic() + 60
    for i in range(5):
        store.set(f"k{i}", _Entry(b"x", "application/json", f'"{i}"', future))
    assert len(store._store) == 2
    # Oldest keys evicted; the two most-recently-set survive.
    assert store.get("k0") is None
    assert store.get("k3") is not None
    assert store.get("k4") is not None


def test_ttlcache_eviction_prunes_expired_first():
    store = TTLCache(max_entries=2)
    now = time.monotonic()
    store.set("stale", _Entry(b"x", "application/json", '"s"', now - 1))
    store.set("fresh", _Entry(b"x", "application/json", '"f"', now + 60))
    store.set("newer", _Entry(b"x", "application/json", '"n"', now + 60))
    assert store.get("stale") is None
    assert store.get("fresh") is not None
    assert store.get("newer") is not None


def test_ttlcache_invalidate_prefix():
    store = TTLCache()
    future = time.monotonic() + 60
    store.set("/api/v1/vehicles?", _Entry(b"a", "application/json", '"1"', future))
    store.set("/api/v1/vehicles/123?", _Entry(b"b", "application/json", '"2"', future))
    store.set("/api/v1/drivers?", _Entry(b"c", "application/json", '"3"', future))

    store.invalidate_prefix("/api/v1/vehicles")

    assert store.get("/api/v1/vehicles?") is None
    assert store.get("/api/v1/vehicles/123?") is None
    assert store.get("/api/v1/drivers?") is not None
