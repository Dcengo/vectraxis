"""Tests for the pipelines router endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_list_pipelines_returns_list(client):
    response = await client.get("/api/v1/pipelines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


async def test_list_pipelines_has_three_entries(client):
    response = await client.get("/api/v1/pipelines/")
    data = response.json()
    assert len(data) == 3


async def test_pipeline_has_name_and_description(client):
    response = await client.get("/api/v1/pipelines/")
    data = response.json()
    for pipeline in data:
        assert "name" in pipeline
        assert "description" in pipeline
        assert isinstance(pipeline["name"], str)
        assert isinstance(pipeline["description"], str)
        assert len(pipeline["name"]) > 0
        assert len(pipeline["description"]) > 0
