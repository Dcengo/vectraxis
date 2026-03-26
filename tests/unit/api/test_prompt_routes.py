"""Tests for the prompts router."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api import dependencies
from vectraxis.api.app import create_app


@pytest.fixture(autouse=True)
def _reset_shared_singletons():
    dependencies._shared_prompt_repo = None
    yield
    dependencies._shared_prompt_repo = None


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _prompt_body(name: str = "test-prompt", **overrides):
    body = {
        "name": name,
        "user_prompt_template": "Analyze {{input}}",
    }
    body.update(overrides)
    return body


class TestPromptRoutes:
    async def test_create_prompt(self, client):
        resp = await client.post("/api/v1/prompts/", json=_prompt_body())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-prompt"
        assert data["id"]
        assert data["version"] == 1

    async def test_list_prompts_empty(self, client):
        resp = await client.get("/api/v1/prompts/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_prompts_returns_created(self, client):
        await client.post("/api/v1/prompts/", json=_prompt_body("a"))
        await client.post("/api/v1/prompts/", json=_prompt_body("b"))
        resp = await client.get("/api/v1/prompts/")
        assert len(resp.json()) == 2

    async def test_list_prompts_filter_by_tags(self, client):
        await client.post(
            "/api/v1/prompts/",
            json=_prompt_body("a", tags=["prod"]),
        )
        await client.post(
            "/api/v1/prompts/",
            json=_prompt_body("b", tags=["dev"]),
        )
        resp = await client.get("/api/v1/prompts/?tags=prod")
        assert len(resp.json()) == 1

    async def test_get_prompt(self, client):
        create = await client.post("/api/v1/prompts/", json=_prompt_body())
        pid = create.json()["id"]
        resp = await client.get(f"/api/v1/prompts/{pid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == pid

    async def test_get_prompt_not_found(self, client):
        resp = await client.get("/api/v1/prompts/nonexistent")
        assert resp.status_code == 404

    async def test_update_prompt(self, client):
        create = await client.post("/api/v1/prompts/", json=_prompt_body())
        pid = create.json()["id"]
        resp = await client.put(
            f"/api/v1/prompts/{pid}",
            json={"name": "updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "updated"
        assert resp.json()["version"] == 2

    async def test_update_prompt_not_found(self, client):
        resp = await client.put(
            "/api/v1/prompts/nonexistent",
            json={"name": "x"},
        )
        assert resp.status_code == 404

    async def test_delete_prompt(self, client):
        create = await client.post("/api/v1/prompts/", json=_prompt_body())
        pid = create.json()["id"]
        resp = await client.delete(f"/api/v1/prompts/{pid}")
        assert resp.status_code == 204
        # Confirm deleted
        resp = await client.get(f"/api/v1/prompts/{pid}")
        assert resp.status_code == 404

    async def test_delete_prompt_not_found(self, client):
        resp = await client.delete("/api/v1/prompts/nonexistent")
        assert resp.status_code == 404
