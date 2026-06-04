"""Async SQLAlchemy engine, session factory and FastAPI dependency."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


engine = create_async_engine(settings.database_url, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a database session scoped to a single request."""
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
