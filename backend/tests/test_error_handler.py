import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.core.errors import register_exception_handlers


@pytest.mark.asyncio
async def test_unhandled_exception_returns_clean_json_500():
    """An uncaught exception is converted to a generic JSON 500 and the raw
    error message is not leaked to the client."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom-secret-detail")

    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "kaboom-secret-detail" not in response.text


@pytest.mark.asyncio
async def test_http_exception_still_passes_through():
    """Registering the catch-all must not swallow normal HTTPExceptions."""
    from fastapi import HTTPException

    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/not-found")
    async def not_found():
        raise HTTPException(status_code=404, detail="nope")

    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/not-found")

    assert response.status_code == 404
    assert response.json() == {"detail": "nope"}
