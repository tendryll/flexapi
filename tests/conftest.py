"""Test fixtures: an isolated in-memory SQLite database per test.

SQLite lets the full request/response path run without a live PostgreSQL
instance. The ORM column mappings are portable, so behaviour matches Postgres
for these tests.
"""

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.database import Base, get_session
from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session() -> AsyncIterator:
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

    app.dependency_overrides.clear()
    await engine.dispose()
