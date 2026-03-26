"""Shared test fixtures for Vectraxis."""

import pytest

from vectraxis.agents.base import FakeLLMProvider
from vectraxis.models.agent import AgentType
from vectraxis.retrieval.chunking import RecursiveChunker
from vectraxis.retrieval.embeddings import FakeEmbeddingProvider
from vectraxis.retrieval.vector_store import InMemoryVectorStore


@pytest.fixture
def fake_llm():
    return FakeLLMProvider(
        responses={
            "analyze": "Analysis complete: workflow shows positive trends.",
            "summarize": "Summary: 15 tasks completed, 5 remaining.",
            "recommend": "Recommendation: automate repetitive data entry tasks.",
        }
    )


@pytest.fixture
def fake_embedder():
    return FakeEmbeddingProvider(dimension=384)


@pytest.fixture
def in_memory_store():
    return InMemoryVectorStore()


@pytest.fixture
def chunker():
    return RecursiveChunker(max_size=200)


@pytest.fixture
def sample_workflow_records():
    return [
        {
            "task_id": "TASK-001",
            "assignee": "Alice",
            "status": "completed",
            "duration_hours": 4.5,
            "description": "Implement login page",
        },
        {
            "task_id": "TASK-002",
            "assignee": "Bob",
            "status": "in_progress",
            "duration_hours": 2.0,
            "description": "Fix search bug",
        },
        {
            "task_id": "TASK-003",
            "assignee": "Alice",
            "status": "blocked",
            "duration_hours": 8.0,
            "description": "Database migration",
        },
    ]


@pytest.fixture
def agent_types():
    return list(AgentType)
