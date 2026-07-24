"""Behave fixtures: run the ASGI app against a fresh in-memory SQLite database.

Mirrors tests/conftest.py — a new database and ``get_session`` override per
scenario — but driven from Behave's synchronous hooks via a single persistent
event loop so all async database work stays on one loop.
"""

import asyncio
import os
import sys
import uuid
from datetime import date

# Make the project's ``src`` directory (two levels up from tests/integration/,
# then into src/) importable as ``app`` even when the package is not installed
# (pyproject sets package = false).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: E402

from app.config.database import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.repository.entity.models import Book  # noqa: E402

# A known book seeded into every scenario's database so the retrieve/update/
# delete scenarios can reference a stable id (see tests/integration/books.feature).
HOBBIT_ID = uuid.UUID("0190a000-0000-7000-8000-0000000000b1")


async def _seed(session_factory) -> None:
    async with session_factory() as session:
        session.add(
            Book(
                id=HOBBIT_ID,
                title="The Hobbit",
                description="Bilbo Baggins goes there and back again.",
                publisher="George Allen & Unwin",
                publishing_date=date(1937, 9, 21),
                page_count=310,
                availability=True,
            )
        )
        await session.commit()


def before_all(context):
    context.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(context.loop)


def after_all(context):
    context.loop.close()


def before_scenario(context, scenario):
    async def setup():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        await _seed(session_factory)

        async def override_get_session():
            async with session_factory() as session:
                yield session

        app.dependency_overrides[get_session] = override_get_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        return engine, client

    context.engine, context.client = context.loop.run_until_complete(setup())
    context.response = None
    context.book_id = None


def after_scenario(context, scenario):
    async def teardown():
        await context.client.aclose()
        await context.engine.dispose()

    context.loop.run_until_complete(teardown())
    app.dependency_overrides.clear()