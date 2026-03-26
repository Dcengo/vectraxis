"""Tests for the query router endpoints."""

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


async def test_query_returns_response(client):
    response = await client.post(
        "/api/v1/query/",
        json={"query": "Analyze workflow efficiency"},
    )
    assert response.status_code == 200


async def test_query_has_output(client):
    response = await client.post(
        "/api/v1/query/",
        json={"query": "Analyze workflow efficiency"},
    )
    data = response.json()
    assert "output" in data
    assert isinstance(data["output"], str)
    assert len(data["output"]) > 0


async def test_query_has_confidence(client):
    response = await client.post(
        "/api/v1/query/",
        json={"query": "Analyze workflow efficiency"},
    )
    data = response.json()
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0


async def test_query_has_steps(client):
    response = await client.post(
        "/api/v1/query/",
        json={"query": "Analyze workflow efficiency"},
    )
    data = response.json()
    assert "steps" in data
    assert isinstance(data["steps"], list)
    assert len(data["steps"]) > 0


async def test_query_with_different_agent_types(client):
    for agent_type in ["analysis", "summarization", "recommendation"]:
        response = await client.post(
            "/api/v1/query/",
            json={"query": "Test query", "agent_type": agent_type},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == agent_type
