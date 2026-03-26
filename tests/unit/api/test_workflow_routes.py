"""Tests for the workflows router."""

import pytest
from httpx import ASGITransport, AsyncClient

from vectraxis.api import dependencies
from vectraxis.api.app import create_app
from vectraxis.models.prompt import Prompt


@pytest.fixture(autouse=True)
def _reset_shared_singletons():
    dependencies._shared_workflow_repo = None
    dependencies._shared_prompt_repo = None
    dependencies._shared_data_source_repo = None
    dependencies._shared_retriever = None
    yield
    dependencies._shared_workflow_repo = None
    dependencies._shared_prompt_repo = None
    dependencies._shared_data_source_repo = None
    dependencies._shared_retriever = None


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _workflow_body(name: str = "test-wf", **overrides):
    body = {
        "name": name,
        "nodes": [
            {"id": "n1", "type": "output", "label": "Output"},
        ],
        "edges": [],
    }
    body.update(overrides)
    return body


class TestWorkflowRoutes:
    async def test_create_workflow(self, client):
        resp = await client.post("/api/v1/workflows/", json=_workflow_body())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-wf"
        assert data["id"]
        assert len(data["nodes"]) == 1

    async def test_list_workflows_empty(self, client):
        resp = await client.get("/api/v1/workflows/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_workflows(self, client):
        await client.post("/api/v1/workflows/", json=_workflow_body("a"))
        await client.post("/api/v1/workflows/", json=_workflow_body("b"))
        resp = await client.get("/api/v1/workflows/")
        assert len(resp.json()) == 2

    async def test_get_workflow(self, client):
        create = await client.post("/api/v1/workflows/", json=_workflow_body())
        wid = create.json()["id"]
        resp = await client.get(f"/api/v1/workflows/{wid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == wid

    async def test_get_workflow_not_found(self, client):
        resp = await client.get("/api/v1/workflows/nonexistent")
        assert resp.status_code == 404

    async def test_update_workflow(self, client):
        create = await client.post("/api/v1/workflows/", json=_workflow_body())
        wid = create.json()["id"]
        resp = await client.put(
            f"/api/v1/workflows/{wid}",
            json={"name": "renamed"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "renamed"
        assert resp.json()["version"] == 2

    async def test_update_workflow_not_found(self, client):
        resp = await client.put(
            "/api/v1/workflows/nonexistent",
            json={"name": "x"},
        )
        assert resp.status_code == 404

    async def test_delete_workflow(self, client):
        create = await client.post("/api/v1/workflows/", json=_workflow_body())
        wid = create.json()["id"]
        resp = await client.delete(f"/api/v1/workflows/{wid}")
        assert resp.status_code == 204
        resp = await client.get(f"/api/v1/workflows/{wid}")
        assert resp.status_code == 404

    async def test_delete_workflow_not_found(self, client):
        resp = await client.delete("/api/v1/workflows/nonexistent")
        assert resp.status_code == 404

    async def test_run_workflow(self, client):
        # First create a prompt
        prompt_repo = dependencies.get_prompt_repo()
        await prompt_repo.create(
            Prompt(
                id="p1",
                name="test",
                user_prompt_template="Do: {{input}}",
            )
        )

        # Create workflow with prompt -> output
        wf_body = {
            "name": "runnable",
            "nodes": [
                {"id": "n1", "type": "prompt", "config": {"prompt_id": "p1"}},
                {"id": "n2", "type": "output"},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
        create = await client.post("/api/v1/workflows/", json=wf_body)
        wid = create.json()["id"]

        resp = await client.post(f"/api/v1/workflows/{wid}/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert len(data["node_results"]) == 2

    async def test_run_nonexistent_workflow(self, client):
        resp = await client.post("/api/v1/workflows/nonexistent/run")
        assert resp.status_code == 404

    async def test_run_workflow_with_failure(self, client):
        """Workflow with bad prompt ref should return failed status."""
        wf_body = {
            "name": "bad",
            "nodes": [
                {"id": "n1", "type": "prompt", "config": {"prompt_id": "nonexistent"}},
                {"id": "n2", "type": "output"},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
        create = await client.post("/api/v1/workflows/", json=wf_body)
        wid = create.json()["id"]

        resp = await client.post(f"/api/v1/workflows/{wid}/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "failed"
