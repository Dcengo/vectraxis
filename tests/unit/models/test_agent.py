"""TDD tests for vectraxis.models.agent module.

Tests define the API contract for:
- AgentType enum
- AgentTask model
- AgentResult model
- PipelineRun model
"""

import pytest
from pydantic import ValidationError

from vectraxis.models.agent import (
    AgentResult,
    AgentTask,
    AgentType,
    PipelineRun,
)
from vectraxis.models.common import (
    Priority,
    TaskStatus,
    VectraxisModel,
    generate_id,
)

# --- AgentType ---


class TestAgentType:
    """Tests for the AgentType enum."""

    def test_has_analysis(self):
        assert AgentType.ANALYSIS is not None

    def test_has_summarization(self):
        assert AgentType.SUMMARIZATION is not None

    def test_has_recommendation(self):
        assert AgentType.RECOMMENDATION is not None

    def test_has_exactly_three_values(self):
        assert len(AgentType) == 3

    def test_values_are_strings(self):
        for t in AgentType:
            assert isinstance(t.value, str)


# --- AgentTask ---


class TestAgentTask:
    """Tests for the AgentTask model."""

    def test_create_with_required_fields(self):
        task = AgentTask(
            id=generate_id(),
            query="Analyze sales trends",
            agent_type=AgentType.ANALYSIS,
        )
        assert task.query == "Analyze sales trends"
        assert task.agent_type == AgentType.ANALYSIS

    def test_context_defaults_to_empty_list(self):
        task = AgentTask(
            id=generate_id(),
            query="query",
            agent_type=AgentType.ANALYSIS,
        )
        assert task.context == []

    def test_context_can_be_set(self):
        ctx = ["doc1 content", "doc2 content"]
        task = AgentTask(
            id=generate_id(),
            query="query",
            agent_type=AgentType.ANALYSIS,
            context=ctx,
        )
        assert task.context == ctx

    def test_priority_defaults_to_medium(self):
        task = AgentTask(
            id=generate_id(),
            query="query",
            agent_type=AgentType.ANALYSIS,
        )
        assert task.priority == Priority.MEDIUM

    def test_priority_can_be_set(self):
        task = AgentTask(
            id=generate_id(),
            query="query",
            agent_type=AgentType.ANALYSIS,
            priority=Priority.CRITICAL,
        )
        assert task.priority == Priority.CRITICAL

    def test_requires_query(self):
        with pytest.raises(ValidationError):
            AgentTask(id=generate_id(), agent_type=AgentType.ANALYSIS)

    def test_requires_agent_type(self):
        with pytest.raises(ValidationError):
            AgentTask(id=generate_id(), query="query")

    def test_invalid_agent_type_raises(self):
        with pytest.raises(ValidationError):
            AgentTask(id=generate_id(), query="query", agent_type="INVALID")

    def test_serialization(self):
        task = AgentTask(
            id="task-1",
            query="summarize",
            agent_type=AgentType.SUMMARIZATION,
            context=["ctx"],
            priority=Priority.HIGH,
        )
        data = task.model_dump()
        assert data["query"] == "summarize"
        assert data["context"] == ["ctx"]

    def test_is_vectraxis_model(self):
        assert issubclass(AgentTask, VectraxisModel)


# --- AgentResult ---


class TestAgentResult:
    """Tests for the AgentResult model."""

    def test_create_with_required_fields(self):
        result = AgentResult(
            id=generate_id(),
            task_id="task-1",
            agent_type=AgentType.ANALYSIS,
            output="Analysis complete: sales up 15%",
            confidence=0.85,
            evidence=["Q1 report", "Q2 report"],
        )
        assert result.output == "Analysis complete: sales up 15%"
        assert result.confidence == 0.85

    def test_confidence_at_zero(self):
        result = AgentResult(
            id=generate_id(),
            task_id="t1",
            agent_type=AgentType.ANALYSIS,
            output="output",
            confidence=0.0,
            evidence=[],
        )
        assert result.confidence == 0.0

    def test_confidence_at_one(self):
        result = AgentResult(
            id=generate_id(),
            task_id="t1",
            agent_type=AgentType.ANALYSIS,
            output="output",
            confidence=1.0,
            evidence=[],
        )
        assert result.confidence == 1.0

    def test_confidence_below_zero_raises(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                task_id="t1",
                agent_type=AgentType.ANALYSIS,
                output="output",
                confidence=-0.1,
                evidence=[],
            )

    def test_confidence_above_one_raises(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                task_id="t1",
                agent_type=AgentType.ANALYSIS,
                output="output",
                confidence=1.1,
                evidence=[],
            )

    def test_evidence_is_list_of_strings(self):
        result = AgentResult(
            id=generate_id(),
            task_id="t1",
            agent_type=AgentType.SUMMARIZATION,
            output="summary",
            confidence=0.9,
            evidence=["source1", "source2"],
        )
        assert result.evidence == ["source1", "source2"]

    def test_requires_task_id(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                agent_type=AgentType.ANALYSIS,
                output="output",
                confidence=0.5,
                evidence=[],
            )

    def test_requires_output(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                task_id="t1",
                agent_type=AgentType.ANALYSIS,
                confidence=0.5,
                evidence=[],
            )

    def test_requires_confidence(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                task_id="t1",
                agent_type=AgentType.ANALYSIS,
                output="output",
                evidence=[],
            )

    def test_requires_evidence(self):
        with pytest.raises(ValidationError):
            AgentResult(
                id=generate_id(),
                task_id="t1",
                agent_type=AgentType.ANALYSIS,
                output="output",
                confidence=0.5,
            )

    def test_serialization(self):
        result = AgentResult(
            id="res-1",
            task_id="task-1",
            agent_type=AgentType.RECOMMENDATION,
            output="recommend X",
            confidence=0.7,
            evidence=["ev1"],
        )
        data = result.model_dump()
        assert data["task_id"] == "task-1"
        assert data["output"] == "recommend X"
        assert data["confidence"] == 0.7
        assert data["evidence"] == ["ev1"]

    def test_is_vectraxis_model(self):
        assert issubclass(AgentResult, VectraxisModel)


# --- PipelineRun ---


class TestPipelineRun:
    """Tests for the PipelineRun model."""

    def test_create_with_required_fields(self):
        run = PipelineRun(
            id=generate_id(),
            query="What are the sales trends?",
            status=TaskStatus.PENDING,
        )
        assert run.query == "What are the sales trends?"
        assert run.status == TaskStatus.PENDING

    def test_steps_defaults_to_empty_list(self):
        run = PipelineRun(
            id=generate_id(),
            query="query",
            status=TaskStatus.PENDING,
        )
        assert run.steps == []

    def test_steps_can_be_set(self):
        steps = ["retrieve", "analyze", "summarize"]
        run = PipelineRun(
            id=generate_id(),
            query="query",
            status=TaskStatus.IN_PROGRESS,
            steps=steps,
        )
        assert run.steps == steps

    def test_result_is_optional(self):
        run = PipelineRun(
            id=generate_id(),
            query="query",
            status=TaskStatus.PENDING,
        )
        assert run.result is None

    def test_result_can_be_set(self):
        agent_result = AgentResult(
            id=generate_id(),
            task_id="t1",
            agent_type=AgentType.ANALYSIS,
            output="done",
            confidence=0.95,
            evidence=["e1"],
        )
        run = PipelineRun(
            id=generate_id(),
            query="query",
            status=TaskStatus.COMPLETED,
            result=agent_result,
        )
        assert run.result is not None
        assert run.result.output == "done"

    def test_requires_query(self):
        with pytest.raises(ValidationError):
            PipelineRun(id=generate_id(), status=TaskStatus.PENDING)

    def test_requires_status(self):
        with pytest.raises(ValidationError):
            PipelineRun(id=generate_id(), query="query")

    def test_status_can_be_any_task_status(self):
        for status in TaskStatus:
            run = PipelineRun(id=generate_id(), query="query", status=status)
            assert run.status == status

    def test_serialization(self):
        run = PipelineRun(
            id="run-1",
            query="test query",
            status=TaskStatus.IN_PROGRESS,
            steps=["step1"],
        )
        data = run.model_dump()
        assert data["query"] == "test query"
        assert data["steps"] == ["step1"]
        assert data["result"] is None

    def test_is_vectraxis_model(self):
        assert issubclass(PipelineRun, VectraxisModel)
