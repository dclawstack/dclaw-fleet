"""In-process per-IP rate limiting.

AI agents make many more requests than humans; without a limit the API can be
overwhelmed and auth endpoints can be brute-forced. This adds a fixed-window
per-IP limiter as the outermost middleware (it runs before the response cache,
so cached hits still count against the budget).

Two tiers: a strict limit on ``/api/v1/auth`` (re-auth / brute-force protection)
and a looser global limit for the rest of ``/api/v1``. ``/health`` is never
limited so it stays usable as a liveness/readiness probe.

The counters are process-local — correct for the current single-replica
deployment. Under multiple replicas each replica enforces its own limit; swap
the ``RateLimiter`` store for a shared backend (e.g. Redis) for a true global
limit. Account lockout on repeated auth failures is a separate stateful concern
and intentionally not handled here.
"""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

_WINDOW_SECONDS = 60
_AUTH_PREFIX = "/api/v1/auth"


class RateLimiter:
    """Fixed-window request counter keyed by ``"<ip>:<bucket>"``."""

    def __init__(self) -> None:
        self._hits: dict[str, tuple[int, float]] = {}

    def check(self, key: str, limit: int) -> tuple[bool, int, int]:
        """Record a hit. Returns ``(allowed, remaining, retry_after)``."""
        now = time.monotonic()
        count, window_start = self._hits.get(key, (0, now))
        if now - window_start >= _WINDOW_SECONDS:
            count, window_start = 0, now

        count += 1
        self._hits[key] = (count, window_start)

        if count > limit:
            retry_after = max(1, int(_WINDOW_SECONDS - (now - window_start)))
            return False, 0, retry_after
        return True, limit - count, 0

    def clear(self) -> None:
        self._hits.clear()


limiter = RateLimiter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not settings.rate_limit_enabled or not path.startswith("/api/v1/"):
            return await call_next(request)

        if path.startswith(_AUTH_PREFIX):
            bucket, limit = "auth", settings.auth_rate_limit_per_minute
        else:
            bucket, limit = "global", settings.rate_limit_per_minute

        key = f"{_client_ip(request)}:{bucket}"
        allowed, remaining, retry_after = limiter.check(key, limit)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def register_rate_limit(app) -> None:
    """Attach the rate-limit middleware. Call last so it sits outermost."""
    app.add_middleware(RateLimitMiddleware)
