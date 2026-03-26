"""Registry for mapping DataSourceType to the appropriate Loader."""

from vectraxis.ingestion.loaders import (
    CSVLoader,
    JSONLoader,
    Loader,
    TextDocumentLoader,
)
from vectraxis.models.ingestion import DataSourceType


class LoaderRegistry:
    """Maps DataSourceType values to Loader instances."""

    def __init__(self) -> None:
        self._loaders: dict[DataSourceType, Loader] = {}

    def register(self, source_type: DataSourceType, loader: Loader) -> None:
        self._loaders[source_type] = loader

    def get(self, source_type: DataSourceType) -> Loader:
        try:
            return self._loaders[source_type]
        except KeyError:
            msg = f"No loader registered for source type: {source_type}"
            raise KeyError(msg) from None


def create_default_registry() -> LoaderRegistry:
    """Create a registry pre-configured with all built-in loaders."""
    registry = LoaderRegistry()
    registry.register(DataSourceType.CSV, CSVLoader())
    registry.register(DataSourceType.JSON, JSONLoader())
    registry.register(DataSourceType.TEXT_DOCUMENT, TextDocumentLoader())
    return registry
