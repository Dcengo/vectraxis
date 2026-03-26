"""Tests for the health check endpoint."""

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


async def test_health_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


async def test_health_has_status_healthy(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "healthy"


async def test_health_has_version(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.1.0"
