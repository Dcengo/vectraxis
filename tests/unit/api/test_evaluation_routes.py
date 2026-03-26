"""Tests for the evaluation router endpoints."""

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


async def test_evaluation_status_returns_200(client):
    response = await client.get("/api/v1/evaluation/status")
    assert response.status_code == 200


async def test_evaluation_status_has_metrics(client):
    response = await client.get("/api/v1/evaluation/status")
    data = response.json()
    assert "available_metrics" in data
    assert isinstance(data["available_metrics"], list)
    assert len(data["available_metrics"]) > 0


async def test_evaluation_status_is_ready(client):
    response = await client.get("/api/v1/evaluation/status")
    data = response.json()
    assert data["status"] == "ready"
