"""Tests for the ingestion router endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api import dependencies
from vectraxis.api.app import create_app


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


async def test_upload_returns_response(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test.csv", b"col1,col2\n1,2", "text/csv")},
    )
    assert response.status_code == 200


async def test_upload_has_source_id(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test.csv", b"col1,col2\n1,2", "text/csv")},
    )
    data = response.json()
    assert "source_id" in data
    assert len(data["source_id"]) > 0


async def test_upload_has_message(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("data.json", b'{"key": "value"}', "application/json")},
    )
    data = response.json()
    assert "message" in data
    assert "data.json" in data["message"]


async def test_upload_csv_processes_records(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test.csv", b"col1,col2\n1,2\n3,4", "text/csv")},
    )
    data = response.json()
    assert data["records_count"] == 2


async def test_upload_json_array_processes_records(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={
            "file": (
                "data.json",
                b'[{"a":1},{"a":2},{"a":3}]',
                "application/json",
            )
        },
    )
    data = response.json()
    assert data["records_count"] == 3


async def test_upload_json_single_object(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("data.json", b'{"key": "value"}', "application/json")},
    )
    data = response.json()
    assert data["records_count"] == 1


async def test_upload_txt_processes_records(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("doc.txt", b"Hello world", "text/plain")},
    )
    data = response.json()
    assert data["records_count"] == 1


async def test_upload_unsupported_type(client):
    response = await client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("data.xyz", b"content", "application/octet-stream")},
    )
    assert response.status_code == 400
