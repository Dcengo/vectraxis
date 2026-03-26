"""Tests for the DataSourceRegistry."""

from vectraxis.api.data_source_registry import DataSourceRegistry
from vectraxis.models.ingestion import DataSource, DataSourceType


class TestDataSourceRegistry:
    def _make_source(self, source_id: str = "s1", name: str = "test.csv") -> DataSource:
        return DataSource(
            id=source_id,
            name=name,
            source_type=DataSourceType.CSV,
            file_path="/tmp/test.csv",
        )

    def test_register_and_get(self):
        reg = DataSourceRegistry()
        src = self._make_source("s1")
        reg.register(src)
        assert reg.get("s1") is src

    def test_get_nonexistent_returns_none(self):
        reg = DataSourceRegistry()
        assert reg.get("missing") is None

    def test_list_all_empty(self):
        reg = DataSourceRegistry()
        assert reg.list_all() == []

    def test_list_all_returns_all(self):
        reg = DataSourceRegistry()
        reg.register(self._make_source("s1", "a.csv"))
        reg.register(self._make_source("s2", "b.csv"))
        assert len(reg.list_all()) == 2

    def test_clear_removes_all(self):
        reg = DataSourceRegistry()
        reg.register(self._make_source("s1"))
        reg.clear()
        assert reg.list_all() == []
        assert reg.get("s1") is None
