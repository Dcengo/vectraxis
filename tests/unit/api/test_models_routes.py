"""Tests for the models and providers router endpoints."""

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


class TestModelsEndpoint:
    """Tests for GET /api/v1/models/."""

    async def test_returns_200(self, client):
        response = await client.get("/api/v1/models/")
        assert response.status_code == 200

    async def test_returns_list(self, client):
        response = await client.get("/api/v1/models/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_model_has_required_fields(self, client):
        response = await client.get("/api/v1/models/")
        data = response.json()
        for item in data:
            assert "model" in item
            assert "provider" in item
            assert "status" in item

    async def test_contains_gpt4o(self, client):
        response = await client.get("/api/v1/models/")
        data = response.json()
        model_names = [m["model"] for m in data]
        assert "gpt-4o" in model_names

    async def test_contains_claude_sonnet(self, client):
        response = await client.get("/api/v1/models/")
        data = response.json()
        model_names = [m["model"] for m in data]
        assert "claude-sonnet-4-20250514" in model_names

    async def test_all_disabled_without_keys(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_XAI_API_KEY", "")
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/models/")
            data = response.json()
            assert all(m["status"] == "disabled" for m in data)


class TestProvidersEndpoint:
    """Tests for GET /api/v1/providers/."""

    async def test_returns_200(self, client):
        response = await client.get("/api/v1/providers/")
        assert response.status_code == 200

    async def test_returns_list(self, client):
        response = await client.get("/api/v1/providers/")
        data = response.json()
        assert isinstance(data, list)

    async def test_has_three_providers(self, client):
        response = await client.get("/api/v1/providers/")
        data = response.json()
        assert len(data) == 3

    async def test_provider_has_required_fields(self, client):
        response = await client.get("/api/v1/providers/")
        data = response.json()
        for item in data:
            assert "name" in item
            assert "status" in item
            assert "models" in item

    async def test_provider_names(self, client):
        response = await client.get("/api/v1/providers/")
        data = response.json()
        names = {p["name"] for p in data}
        assert names == {"openai", "anthropic", "xai"}

    async def test_providers_have_models(self, client):
        response = await client.get("/api/v1/providers/")
        data = response.json()
        for item in data:
            assert len(item["models"]) > 0


class TestQueryModelParam:
    """Tests for model param in query endpoint."""

    async def test_query_response_has_model_field(self, client):
        response = await client.post(
            "/api/v1/query/",
            json={"query": "Test query"},
        )
        data = response.json()
        assert "model" in data

    async def test_query_without_model_uses_fake(self, client):
        response = await client.post(
            "/api/v1/query/",
            json={"query": "Test query"},
        )
        data = response.json()
        assert data["model"] == "fake"

    async def test_query_with_unknown_model_falls_back_to_fake(self, client):
        response = await client.post(
            "/api/v1/query/",
            json={"query": "Test query", "model": "nonexistent"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "fake"
