"""Tests for the data sources router."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api import dependencies
from vectraxis.api.app import create_app
from vectraxis.db.repositories.data_source import InMemoryDataSourceRepository
from vectraxis.models.ingestion import DataSource, DataSourceType


@pytest.fixture(autouse=True)
def _reset_shared_singletons():
    """Reset shared singletons between tests."""
    dependencies._shared_retriever = None
    dependencies._shared_data_source_registry = None
    dependencies._shared_data_source_repo = None
    yield
    dependencies._shared_retriever = None
    dependencies._shared_data_source_registry = None
    dependencies._shared_data_source_repo = None


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_list_data_sources_empty(client):
    response = await client.get("/api/v1/data-sources/")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_data_sources_returns_registered(client):
    repo = dependencies.get_data_source_repo()
    assert isinstance(repo, InMemoryDataSourceRepository)
    await repo.create(
        DataSource(
            id="ds-1",
            name="sales.csv",
            source_type=DataSourceType.CSV,
            file_path="/tmp/sales.csv",
            metadata={"record_count": 42},
        )
    )
    response = await client.get("/api/v1/data-sources/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "ds-1"
    assert data[0]["name"] == "sales.csv"
    assert data[0]["record_count"] == 42


async def test_list_data_sources_multiple(client):
    repo = dependencies.get_data_source_repo()
    await repo.create(
        DataSource(
            id="ds-1",
            name="a.csv",
            source_type=DataSourceType.CSV,
            file_path="/tmp/a.csv",
            metadata={"record_count": 10},
        )
    )
    await repo.create(
        DataSource(
            id="ds-2",
            name="b.json",
            source_type=DataSourceType.JSON,
            file_path="/tmp/b.json",
            metadata={"record_count": 5},
        )
    )
    response = await client.get("/api/v1/data-sources/")
    assert response.status_code == 200
    assert len(response.json()) == 2
