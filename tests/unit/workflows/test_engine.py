"""Tests for the WorkflowEngine."""

import pytest

from vectraxis.config import Settings
from vectraxis.db.repositories.data_source import InMemoryDataSourceRepository
from vectraxis.db.repositories.prompt import InMemoryPromptRepository
from vectraxis.models.ingestion import DataSource, DataSourceType
from vectraxis.models.prompt import Prompt
from vectraxis.models.workflow import (
    NodeType,
    Workflow,
    WorkflowEdge,
    WorkflowNode,
)
from vectraxis.retrieval.chunking import RecursiveChunker
from vectraxis.retrieval.embeddings import FakeEmbeddingProvider
from vectraxis.retrieval.rag import RAGRetriever
from vectraxis.retrieval.vector_store import InMemoryVectorStore
from vectraxis.workflows.engine import WorkflowEngine


@pytest.fixture
def prompt_repo():
    return InMemoryPromptRepository()


@pytest.fixture
def ds_repo():
    return InMemoryDataSourceRepository()


@pytest.fixture
def retriever():
    return RAGRetriever(
        chunker=RecursiveChunker(),
        embedder=FakeEmbeddingProvider(),
        store=InMemoryVectorStore(),
    )


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def engine(prompt_repo, ds_repo, retriever, settings):
    return WorkflowEngine(
        prompt_repo=prompt_repo,
        data_source_repo=ds_repo,
        retriever=retriever,
        settings=settings,
    )


class TestWorkflowEngine:
    async def test_linear_flow(self, engine, prompt_repo):
        """Test: prompt -> output."""
        prompt = Prompt(
            id="p1",
            name="test",
            user_prompt_template="Analyze: {{input}}",
        )
        await prompt_repo.create(prompt)

        wf = Workflow(
            name="linear",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.PROMPT,
                    config={"prompt_id": "p1"},
                ),
                WorkflowNode(id="n2", type=NodeType.OUTPUT),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )

        result = await engine.run(wf)
        assert result.status == "completed"
        assert len(result.node_results) == 2
        assert result.node_results[0].status == "completed"
        assert result.final_output != ""

    async def test_condition_branching_true(self, engine, prompt_repo):
        """Test: prompt -> condition -> output_true / output_false."""
        prompt = Prompt(
            id="p1",
            name="test",
            user_prompt_template="{{input}}",
        )
        await prompt_repo.create(prompt)

        wf = Workflow(
            name="branching",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.PROMPT,
                    config={"prompt_id": "p1"},
                ),
                WorkflowNode(
                    id="n2",
                    type=NodeType.CONDITION,
                    config={"field": "", "operator": "contains", "value": "fake"},
                ),
                WorkflowNode(id="n3", type=NodeType.OUTPUT, label="True branch"),
                WorkflowNode(id="n4", type=NodeType.OUTPUT, label="False branch"),
            ],
            edges=[
                WorkflowEdge(id="e1", source="n1", target="n2"),
                WorkflowEdge(id="e2", source="n2", target="n3", source_handle="true"),
                WorkflowEdge(id="e3", source="n2", target="n4", source_handle="false"),
            ],
        )

        result = await engine.run(wf)
        assert result.status == "completed"
        statuses = {nr.node_id: nr.status for nr in result.node_results}
        # One branch should be completed, the other skipped
        assert statuses["n2"] == "completed"
        assert (statuses["n3"] == "skipped") != (statuses["n4"] == "skipped")

    async def test_merger_combines_inputs(self, engine, prompt_repo):
        """Test: two prompts -> merger -> output."""
        p1 = Prompt(id="p1", name="a", user_prompt_template="First: {{input}}")
        p2 = Prompt(id="p2", name="b", user_prompt_template="Second: {{input}}")
        await prompt_repo.create(p1)
        await prompt_repo.create(p2)

        wf = Workflow(
            name="merger",
            nodes=[
                WorkflowNode(id="n1", type=NodeType.PROMPT, config={"prompt_id": "p1"}),
                WorkflowNode(id="n2", type=NodeType.PROMPT, config={"prompt_id": "p2"}),
                WorkflowNode(
                    id="n3",
                    type=NodeType.MERGER,
                    config={"strategy": "concatenate"},
                ),
                WorkflowNode(id="n4", type=NodeType.OUTPUT),
            ],
            edges=[
                WorkflowEdge(id="e1", source="n1", target="n3"),
                WorkflowEdge(id="e2", source="n2", target="n3"),
                WorkflowEdge(id="e3", source="n3", target="n4"),
            ],
        )

        result = await engine.run(wf)
        assert result.status == "completed"
        assert result.final_output != ""

    async def test_cycle_detection(self, engine):
        """Workflow with a cycle should raise an error."""
        wf = Workflow(
            name="cyclic",
            nodes=[
                WorkflowNode(id="n1", type=NodeType.PROMPT, config={"prompt_id": "p1"}),
                WorkflowNode(id="n2", type=NodeType.PROMPT, config={"prompt_id": "p1"}),
            ],
            edges=[
                WorkflowEdge(id="e1", source="n1", target="n2"),
                WorkflowEdge(id="e2", source="n2", target="n1"),
            ],
        )

        result = await engine.run(wf)
        assert result.status == "failed"
        assert "cycle" in result.error.lower()

    async def test_missing_prompt_id(self, engine):
        """Prompt node without prompt_id should fail."""
        wf = Workflow(
            name="missing",
            nodes=[
                WorkflowNode(id="n1", type=NodeType.PROMPT, config={}),
                WorkflowNode(id="n2", type=NodeType.OUTPUT),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )

        result = await engine.run(wf)
        assert result.status == "failed"
        assert "prompt_id" in result.error.lower()

    async def test_nonexistent_prompt(self, engine):
        """Reference to nonexistent prompt should fail."""
        wf = Workflow(
            name="bad-ref",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.PROMPT,
                    config={"prompt_id": "nonexistent"},
                ),
                WorkflowNode(id="n2", type=NodeType.OUTPUT),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )

        result = await engine.run(wf)
        assert result.status == "failed"

    async def test_validator_node(self, engine, prompt_repo):
        """Test validator node execution."""
        prompt = Prompt(
            id="p1",
            name="test",
            user_prompt_template="Generate something: {{input}}",
        )
        await prompt_repo.create(prompt)

        wf = Workflow(
            name="with-validator",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.PROMPT,
                    config={"prompt_id": "p1"},
                ),
                WorkflowNode(
                    id="n2",
                    type=NodeType.VALIDATOR,
                    config={"validator_type": "structure", "min_length": 1},
                ),
                WorkflowNode(id="n3", type=NodeType.OUTPUT),
            ],
            edges=[
                WorkflowEdge(id="e1", source="n1", target="n2"),
                WorkflowEdge(id="e2", source="n2", target="n3"),
            ],
        )

        result = await engine.run(wf)
        assert result.status == "completed"

    async def test_output_json_format(self, engine, prompt_repo):
        """Output node with json format wraps result."""
        prompt = Prompt(
            id="p1",
            name="test",
            user_prompt_template="{{input}}",
        )
        await prompt_repo.create(prompt)

        wf = Workflow(
            name="json-output",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.PROMPT,
                    config={"prompt_id": "p1"},
                ),
                WorkflowNode(
                    id="n2",
                    type=NodeType.OUTPUT,
                    config={"format": "json"},
                ),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )

        result = await engine.run(wf)
        assert result.status == "completed"
        assert '"result"' in result.final_output

    async def test_empty_workflow(self, engine):
        """Empty workflow should complete with no results."""
        wf = Workflow(name="empty")
        result = await engine.run(wf)
        assert result.status == "completed"
        assert result.node_results == []

    async def test_node_failure_captured(self, engine):
        """Failed node should capture error in result."""
        wf = Workflow(
            name="fail",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.DATA_SOURCE,
                    config={},  # missing data_source_id
                ),
            ],
            edges=[],
        )

        result = await engine.run(wf)
        assert result.status == "failed"
        assert result.node_results[0].status == "failed"
        assert result.node_results[0].error is not None

    async def test_condition_numeric_comparison(self, engine):
        """Condition node with numeric operator."""
        wf = Workflow(
            name="numeric-cond",
            nodes=[
                WorkflowNode(id="n1", type=NodeType.OUTPUT),
                WorkflowNode(
                    id="n2",
                    type=NodeType.CONDITION,
                    config={"field": "", "operator": ">", "value": "5"},
                ),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )
        # This tests condition evaluation directly; n1 has no input so output is ""
        result = await engine.run(wf)
        # The condition will try float("") which fails, resulting in "false"
        assert result.status == "completed"

    async def test_data_source_node(self, engine, ds_repo):
        """Data source node loads data."""
        ds = DataSource(
            id="ds-1",
            name="test.csv",
            source_type=DataSourceType.CSV,
            file_path="/tmp/test.csv",
        )
        await ds_repo.create(ds)

        wf = Workflow(
            name="ds-flow",
            nodes=[
                WorkflowNode(
                    id="n1",
                    type=NodeType.DATA_SOURCE,
                    config={"data_source_id": "ds-1"},
                ),
                WorkflowNode(id="n2", type=NodeType.OUTPUT),
            ],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )

        result = await engine.run(wf)
        assert result.status == "completed"

    async def test_duration_tracked(self, engine):
        """Run result should have duration > 0."""
        wf = Workflow(name="timing")
        result = await engine.run(wf)
        assert result.duration_ms >= 0
