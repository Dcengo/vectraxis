"""Tests for Pipeline."""

from dataclasses import dataclass

from vectraxis.agents.base import FakeLLMProvider
from vectraxis.agents.pipeline import Pipeline
from vectraxis.agents.router import TaskRouter
from vectraxis.agents.specialized.analysis import AnalysisAgent
from vectraxis.agents.specialized.recommendation import RecommendationAgent
from vectraxis.agents.specialized.summarization import SummarizationAgent
from vectraxis.models.agent import AgentType, PipelineRun
from vectraxis.models.common import TaskStatus
from vectraxis.models.retrieval import Chunk, SearchResult


@dataclass
class FakeRetriever:
    """Fake retriever for testing pipeline context retrieval."""

    results: list[SearchResult]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        source_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        return self.results


def _build_pipeline(retriever=None) -> Pipeline:
    llm = FakeLLMProvider()
    agents = {
        AgentType.ANALYSIS: AnalysisAgent(llm=llm),
        AgentType.SUMMARIZATION: SummarizationAgent(llm=llm),
        AgentType.RECOMMENDATION: RecommendationAgent(llm=llm),
    }
    router = TaskRouter(agents=agents)
    return Pipeline(router=router, retriever=retriever)


class TestPipeline:
    def test_pipeline_run_creates_pipeline_run(self) -> None:
        pipeline = _build_pipeline()
        result = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert isinstance(result, PipelineRun)

    def test_pipeline_run_has_steps(self) -> None:
        pipeline = _build_pipeline()
        result = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert "query_understanding" in result.steps
        assert "task_creation" in result.steps
        assert "agent_execution" in result.steps
        assert "completed" in result.steps

    def test_pipeline_run_returns_completed_status(self) -> None:
        pipeline = _build_pipeline()
        result = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert result.status == TaskStatus.COMPLETED

    def test_pipeline_run_has_result(self) -> None:
        pipeline = _build_pipeline()
        run = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert run.result is not None
        assert run.result.agent_type == AgentType.ANALYSIS
        assert run.result.output == "This is a fake response."

    def test_pipeline_run_with_retriever(self) -> None:
        chunk = Chunk(document_id="doc1", content="relevant content", index=0)
        search_result = SearchResult(chunk=chunk, score=0.9)
        retriever = FakeRetriever(results=[search_result])
        pipeline = _build_pipeline(retriever=retriever)
        run = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert "context_retrieval" in run.steps
        assert run.result is not None
        assert run.result.evidence == ["relevant content"]

    def test_pipeline_run_without_retriever(self) -> None:
        pipeline = _build_pipeline(retriever=None)
        run = pipeline.run(query="test query", agent_type=AgentType.ANALYSIS)
        assert "context_retrieval" not in run.steps
        assert run.result is not None
        assert run.result.evidence == []
