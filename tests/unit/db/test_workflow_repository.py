"""Tests for the InMemoryWorkflowRepository."""

import pytest

from vectraxis.db.repositories.workflow import (
    InMemoryWorkflowRepository,
    WorkflowRepository,
)
from vectraxis.models.workflow import (
    NodeType,
    Workflow,
    WorkflowEdge,
    WorkflowNode,
)


def _make_workflow(
    workflow_id: str = "wf-1",
    name: str = "test-workflow",
) -> Workflow:
    return Workflow(
        id=workflow_id,
        name=name,
        nodes=[
            WorkflowNode(id="n1", type=NodeType.PROMPT, label="Prompt 1"),
            WorkflowNode(id="n2", type=NodeType.OUTPUT, label="Output"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="n1", target="n2"),
        ],
    )


@pytest.fixture
def repo():
    return InMemoryWorkflowRepository()


class TestInMemoryWorkflowRepository:
    async def test_implements_protocol(self, repo):
        assert isinstance(repo, WorkflowRepository)

    async def test_create_and_get(self, repo):
        wf = _make_workflow("wf-1")
        result = await repo.create(wf)
        assert result.id == "wf-1"
        fetched = await repo.get("wf-1")
        assert fetched is not None
        assert fetched.name == "test-workflow"
        assert len(fetched.nodes) == 2

    async def test_get_nonexistent(self, repo):
        assert await repo.get("missing") is None

    async def test_list_all(self, repo):
        await repo.create(_make_workflow("wf-1", "a"))
        await repo.create(_make_workflow("wf-2", "b"))
        assert len(await repo.list_all()) == 2

    async def test_update(self, repo):
        await repo.create(_make_workflow("wf-1"))
        updated = await repo.update("wf-1", name="renamed")
        assert updated is not None
        assert updated.name == "renamed"
        assert updated.version == 2

    async def test_update_nonexistent(self, repo):
        assert await repo.update("missing", name="x") is None

    async def test_delete(self, repo):
        await repo.create(_make_workflow("wf-1"))
        assert await repo.delete("wf-1") is True
        assert await repo.get("wf-1") is None

    async def test_delete_nonexistent(self, repo):
        assert await repo.delete("missing") is False
