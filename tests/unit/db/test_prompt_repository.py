"""Tests for the InMemoryPromptRepository."""

import pytest

from vectraxis.db.repositories.prompt import (
    InMemoryPromptRepository,
    PromptRepository,
)
from vectraxis.models.prompt import Prompt


def _make_prompt(
    prompt_id: str = "p-1",
    name: str = "test-prompt",
    tags: list[str] | None = None,
) -> Prompt:
    return Prompt(
        id=prompt_id,
        name=name,
        user_prompt_template="Analyze {{input}}",
        tags=tags or [],
    )


@pytest.fixture
def repo():
    return InMemoryPromptRepository()


class TestInMemoryPromptRepository:
    async def test_implements_protocol(self, repo):
        assert isinstance(repo, PromptRepository)

    async def test_create_and_get(self, repo):
        p = _make_prompt("p-1")
        result = await repo.create(p)
        assert result.id == "p-1"
        fetched = await repo.get("p-1")
        assert fetched is not None
        assert fetched.name == "test-prompt"

    async def test_get_nonexistent(self, repo):
        assert await repo.get("missing") is None

    async def test_get_by_name(self, repo):
        await repo.create(_make_prompt("p-1", "my-prompt"))
        found = await repo.get_by_name("my-prompt")
        assert found is not None
        assert found.id == "p-1"

    async def test_get_by_name_not_found(self, repo):
        assert await repo.get_by_name("nope") is None

    async def test_list_all(self, repo):
        await repo.create(_make_prompt("p-1", "a"))
        await repo.create(_make_prompt("p-2", "b"))
        assert len(await repo.list_all()) == 2

    async def test_list_all_with_tags(self, repo):
        await repo.create(_make_prompt("p-1", "a", tags=["analysis"]))
        await repo.create(_make_prompt("p-2", "b", tags=["summary"]))
        results = await repo.list_all(tags=["analysis"])
        assert len(results) == 1
        assert results[0].id == "p-1"

    async def test_update(self, repo):
        await repo.create(_make_prompt("p-1"))
        updated = await repo.update("p-1", name="new-name")
        assert updated is not None
        assert updated.name == "new-name"
        assert updated.version == 2

    async def test_update_nonexistent(self, repo):
        assert await repo.update("missing", name="x") is None

    async def test_delete(self, repo):
        await repo.create(_make_prompt("p-1"))
        assert await repo.delete("p-1") is True
        assert await repo.get("p-1") is None

    async def test_delete_nonexistent(self, repo):
        assert await repo.delete("missing") is False
