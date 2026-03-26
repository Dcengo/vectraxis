"""Async SQLAlchemy session factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from vectraxis.config import Settings


def create_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory from application settings."""
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )
    return async_sessionmaker(engine, expire_on_commit=False)
