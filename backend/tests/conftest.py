import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.api.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User
from app.services.auth import create_access_token, hash_password

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_app_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "test-pass"


async def override_get_db():
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Seed a test admin so every test can authenticate.
    async with AsyncSession(test_engine, expire_on_commit=False) as s:
        admin = User(
            email=TEST_ADMIN_EMAIL,
            name="Test Admin",
            password_hash=hash_password(TEST_ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        s.add(admin)
        await s.commit()

    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Pre-authenticated client. The Authorization header is attached for the
    seeded test admin so domain tests don't have to log in themselves."""
    async with AsyncSession(test_engine, expire_on_commit=False) as s:
        from sqlalchemy import select

        result = await s.execute(select(User).where(User.email == TEST_ADMIN_EMAIL))
        admin = result.scalar_one()
        token, _ = create_access_token(subject=str(admin.id), extra={"role": admin.role})

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def anon_client():
    """Unauthenticated client for testing 401 paths."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
