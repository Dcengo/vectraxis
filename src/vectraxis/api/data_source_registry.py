"""In-memory registry for tracking uploaded data sources."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectraxis.models.ingestion import DataSource


class DataSourceRegistry:
    """Stores DataSource objects in memory for listing and lookup."""

    def __init__(self) -> None:
        self._sources: dict[str, DataSource] = {}

    def register(self, source: DataSource) -> None:
        """Register a data source."""
        self._sources[source.id] = source

    def list_all(self) -> list[DataSource]:
        """Return all registered data sources."""
        return list(self._sources.values())

    def get(self, source_id: str) -> DataSource | None:
        """Return a data source by ID, or None if not found."""
        return self._sources.get(source_id)

    def clear(self) -> None:
        """Remove all registered data sources."""
        self._sources.clear()
