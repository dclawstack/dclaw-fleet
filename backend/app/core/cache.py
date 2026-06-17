"""In-process response caching for read endpoints.

AI agents tend to re-query the same list/detail endpoints repeatedly; without a
cache every call hits the database. This adds a small in-memory TTL cache in
front of ``GET`` responses under ``/api/v1`` (skipping auth/demo), plus
``ETag``/``304`` handling so unchanged payloads cost almost nothing.

The store is process-local — correct for the current single-replica deployment.
If the app is scaled to multiple replicas, swap ``TTLCache`` for a shared
backend (e.g. Redis) behind the same ``get``/``set``/``invalidate_prefix`` API.

Writes (POST/PUT/PATCH/DELETE) invalidate every cached entry under the same
``/api/v1/<resource>`` prefix, so mutations are reflected immediately rather
than waiting out the TTL.
"""
import hashlib
import time
from collections import OrderedDict
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class _Entry:
    __slots__ = ("body", "media_type", "etag", "expires_at")

    def __init__(self, body: bytes, media_type: str, etag: str, expires_at: float):
        self.body = body
        self.media_type = media_type
        self.etag = etag
        self.expires_at = expires_at


class TTLCache:
    """Tiny time-based cache keyed by request path+query.

    Bounded to ``max_entries`` so it can't grow without limit under load: on
    insert, expired entries are pruned first and the least-recently-used entry
    is evicted if the cap is still exceeded.
    """

    def __init__(self, max_entries: int = 1000) -> None:
        self._store: "OrderedDict[str, _Entry]" = OrderedDict()
        self._max_entries = max_entries

    def get(self, key: str) -> Optional[_Entry]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.monotonic():
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return entry

    def set(self, key: str, entry: _Entry) -> None:
        self._store[key] = entry
        self._store.move_to_end(key)
        self._evict()

    def _evict(self) -> None:
        if len(self._store) <= self._max_entries:
            return
        now = time.monotonic()
        for key in [k for k, e in self._store.items() if e.expires_at <= now]:
            self._store.pop(key, None)
        while len(self._store) > self._max_entries:
            self._store.popitem(last=False)

    def invalidate_prefix(self, prefix: str) -> None:
        for key in [k for k in self._store if k.startswith(prefix)]:
            self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


cache = TTLCache(settings.cache_max_entries)


def _resource_prefix(path: str) -> str:
    """``/api/v1/vehicles/123`` -> ``/api/v1/vehicles`` (the cache-key root)."""
    parts = path.split("/")
    return "/".join(parts[:4])


def _is_cacheable_path(path: str) -> bool:
    return (
        path.startswith("/api/v1/")
        and not path.startswith("/api/v1/auth")
        and not path.startswith("/api/v1/demo")
    )


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.cache_enabled or not _is_cacheable_path(request.url.path):
            return await call_next(request)

        if request.method in _WRITE_METHODS:
            response = await call_next(request)
            if response.status_code < 400:
                cache.invalidate_prefix(_resource_prefix(request.url.path))
            return response

        if request.method != "GET":
            return await call_next(request)

        key = f"{request.url.path}?{request.url.query}"
        entry = cache.get(key)
        if entry is not None:
            return self._respond(entry, request, hit=True)

        response = await call_next(request)
        if response.status_code != 200:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        etag = '"' + hashlib.sha256(body).hexdigest()[:16] + '"'
        entry = _Entry(
            body=body,
            media_type=response.media_type or "application/json",
            etag=etag,
            expires_at=time.monotonic() + settings.cache_ttl_seconds,
        )
        cache.set(key, entry)
        return self._respond(entry, request, hit=False)

    def _respond(self, entry: _Entry, request: Request, hit: bool) -> Response:
        headers = {
            "ETag": entry.etag,
            "Cache-Control": f"private, max-age={settings.cache_ttl_seconds}",
            "X-Cache": "HIT" if hit else "MISS",
        }
        if request.headers.get("if-none-match") == entry.etag:
            return Response(status_code=304, headers=headers)
        return Response(
            content=entry.body,
            status_code=200,
            media_type=entry.media_type,
            headers=headers,
        )


def register_cache(app) -> None:
    """Attach the response cache middleware to ``app``."""
    app.add_middleware(ResponseCacheMiddleware)
