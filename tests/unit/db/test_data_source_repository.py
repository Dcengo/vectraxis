"""Tests for the InMemoryDataSourceRepository."""

import pytest

from vectraxis.db.repositories.data_source import (
    DataSourceRepository,
    InMemoryDataSourceRepository,
)
from vectraxis.models.ingestion import DataSource, DataSourceType


def _make_source(source_id: str = "ds-1", name: str = "test.csv") -> DataSource:
    return DataSource(
        id=source_id,
        name=name,
        source_type=DataSourceType.CSV,
        file_path="/tmp/test.csv",
        metadata={"record_count": 10},
        record_count=10,
    )


@pytest.fixture
def repo():
    return InMemoryDataSourceRepository()


class TestInMemoryDataSourceRepository:
    async def test_implements_protocol(self, repo):
        assert isinstance(repo, DataSourceRepository)

    async def test_create_and_get(self, repo):
        ds = _make_source("ds-1")
        result = await repo.create(ds)
        assert result.id == "ds-1"
        fetched = await repo.get("ds-1")
        assert fetched is not None
        assert fetched.name == "test.csv"

    async def test_get_nonexistent_returns_none(self, repo):
        assert await repo.get("missing") is None

    async def test_list_all_empty(self, repo):
        assert await repo.list_all() == []

    async def test_list_all_returns_all(self, repo):
        await repo.create(_make_source("ds-1", "a.csv"))
        await repo.create(_make_source("ds-2", "b.csv"))
        sources = await repo.list_all()
        assert len(sources) == 2

    async def test_delete_existing(self, repo):
        await repo.create(_make_source("ds-1"))
        assert await repo.delete("ds-1") is True
        assert await repo.get("ds-1") is None

    async def test_delete_nonexistent(self, repo):
        assert await repo.delete("missing") is False
