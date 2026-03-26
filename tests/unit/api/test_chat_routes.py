"""Tests for the chat router."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api import dependencies
from vectraxis.api.app import create_app
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


async def _register_source(source_id: str = "ds-1", name: str = "sales.csv"):
    repo = dependencies.get_data_source_repo()
    await repo.create(
        DataSource(
            id=source_id,
            name=name,
            source_type=DataSourceType.CSV,
            file_path="/tmp/test.csv",
            metadata={"record_count": 10},
        )
    )


async def test_chat_basic_message(client):
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello world"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello world"
    assert "response" in data
    assert "steps" in data


async def test_chat_with_data_source(client):
    await _register_source("ds-1", "sales.csv")
    response = await client.post(
        "/api/v1/chat/",
        json={
            "message": "Analyse @sales",
            "data_sources": [{"data_source_id": "ds-1", "data_source_name": "sales"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data_sources_used"]) == 1
    assert data["data_sources_used"][0]["id"] == "ds-1"


async def test_chat_nonexistent_data_source_returns_404(client):
    response = await client.post(
        "/api/v1/chat/",
        json={
            "message": "Analyse @missing",
            "data_sources": [
                {"data_source_id": "nonexistent", "data_source_name": "missing"}
            ],
        },
    )
    assert response.status_code == 404


async def test_chat_with_agent_type(client):
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "Summarize this", "agent_type": "summarization"},
    )
    assert response.status_code == 200


async def test_chat_response_has_model(client):
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "test"},
    )
    data = response.json()
    assert "model" in data


async def test_chat_response_has_confidence(client):
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "test"},
    )
    data = response.json()
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
