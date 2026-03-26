"""Tests for the async session factory."""

from unittest.mock import patch

from sqlalchemy.ext.asyncio import async_sessionmaker

from vectraxis.config import Settings
from vectraxis.db.session import create_session_factory


class TestCreateSessionFactory:
    def test_returns_sessionmaker(self):
        settings = Settings()
        factory = create_session_factory(settings)
        assert isinstance(factory, async_sessionmaker)

    def test_uses_database_url(self):
        settings = Settings(database_url="postgresql+asyncpg://user:pw@host/db")
        with patch("vectraxis.db.session.create_async_engine") as mock_engine:
            create_session_factory(settings)
            mock_engine.assert_called_once()
            args, kwargs = mock_engine.call_args
            assert args[0] == "postgresql+asyncpg://user:pw@host/db"

    def test_debug_enables_echo(self):
        settings = Settings(debug=True)
        with patch("vectraxis.db.session.create_async_engine") as mock_engine:
            create_session_factory(settings)
            _, kwargs = mock_engine.call_args
            assert kwargs["echo"] is True
