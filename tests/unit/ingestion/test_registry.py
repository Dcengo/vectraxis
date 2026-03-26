"""Tests for loader registry - written BEFORE implementation (TDD)."""

import pytest

from vectraxis.ingestion.loaders import (
    CSVLoader,
    JSONLoader,
    TextDocumentLoader,
)
from vectraxis.ingestion.registry import LoaderRegistry, create_default_registry
from vectraxis.models.ingestion import DataSourceType


class TestLoaderRegistry:
    def test_register_and_get_loader(self):
        registry = LoaderRegistry()
        loader = CSVLoader()
        registry.register(DataSourceType.CSV, loader)
        assert registry.get(DataSourceType.CSV) is loader

    def test_get_unregistered_raises(self):
        registry = LoaderRegistry()
        with pytest.raises(KeyError):
            registry.get(DataSourceType.CSV)

    def test_default_registry_has_all_loaders(self):
        registry = create_default_registry()
        csv_loader = registry.get(DataSourceType.CSV)
        json_loader = registry.get(DataSourceType.JSON)
        text_loader = registry.get(DataSourceType.TEXT_DOCUMENT)

        assert isinstance(csv_loader, CSVLoader)
        assert isinstance(json_loader, JSONLoader)
        assert isinstance(text_loader, TextDocumentLoader)
