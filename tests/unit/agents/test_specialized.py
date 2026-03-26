"""Tests for specialized agents: Analysis, Summarization, Recommendation."""

from vectraxis.agents.base import Agent, FakeLLMProvider
from vectraxis.models.agent import AgentResult, AgentTask, AgentType

# --- AnalysisAgent Tests ---


class TestAnalysisAgent:
    def test_analysis_agent_implements_protocol(self) -> None:
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        agent = AnalysisAgent(llm=FakeLLMProvider())
        assert isinstance(agent, Agent)

    def test_analysis_agent_type(self) -> None:
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        agent = AnalysisAgent(llm=FakeLLMProvider())
        assert agent.agent_type == AgentType.ANALYSIS

    def test_analysis_agent_execute_returns_result(self) -> None:
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        agent = AnalysisAgent(llm=FakeLLMProvider())
        task = AgentTask(query="test query", agent_type=AgentType.ANALYSIS)
        result = agent.execute(task)
        assert isinstance(result, AgentResult)

    def test_analysis_agent_uses_llm(self) -> None:
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        llm = FakeLLMProvider(responses={"Analyze": "deep analysis"})
        agent = AnalysisAgent(llm=llm)
        task = AgentTask(query="test query", agent_type=AgentType.ANALYSIS)
        result = agent.execute(task)
        assert result.output == "deep analysis"

    def test_analysis_agent_passes_context(self) -> None:
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        llm = FakeLLMProvider(responses={"Analyze": "contextual analysis"})
        agent = AnalysisAgent(llm=llm)
        task = AgentTask(query="test", agent_type=AgentType.ANALYSIS)
        context = ["doc1", "doc2"]
        result = agent.execute(task, context=context)
        assert result.output == "contextual analysis"
        assert result.evidence == context


# --- SummarizationAgent Tests ---


class TestSummarizationAgent:
    def test_summarization_agent_implements_protocol(self) -> None:
        from vectraxis.agents.specialized.summarization import SummarizationAgent

        agent = SummarizationAgent(llm=FakeLLMProvider())
        assert isinstance(agent, Agent)

    def test_summarization_agent_type(self) -> None:
        from vectraxis.agents.specialized.summarization import SummarizationAgent

        agent = SummarizationAgent(llm=FakeLLMProvider())
        assert agent.agent_type == AgentType.SUMMARIZATION

    def test_summarization_agent_execute_returns_result(self) -> None:
        from vectraxis.agents.specialized.summarization import SummarizationAgent

        agent = SummarizationAgent(llm=FakeLLMProvider())
        task = AgentTask(query="test query", agent_type=AgentType.SUMMARIZATION)
        result = agent.execute(task)
        assert isinstance(result, AgentResult)

    def test_summarization_agent_uses_llm(self) -> None:
        from vectraxis.agents.specialized.summarization import SummarizationAgent

        llm = FakeLLMProvider(responses={"Summarize": "brief summary"})
        agent = SummarizationAgent(llm=llm)
        task = AgentTask(query="test query", agent_type=AgentType.SUMMARIZATION)
        result = agent.execute(task)
        assert result.output == "brief summary"

    def test_summarization_agent_passes_context(self) -> None:
        from vectraxis.agents.specialized.summarization import SummarizationAgent

        llm = FakeLLMProvider(responses={"Summarize": "contextual summary"})
        agent = SummarizationAgent(llm=llm)
        task = AgentTask(query="test", agent_type=AgentType.SUMMARIZATION)
        context = ["doc1", "doc2"]
        result = agent.execute(task, context=context)
        assert result.output == "contextual summary"
        assert result.evidence == context


# --- RecommendationAgent Tests ---


class TestRecommendationAgent:
    def test_recommendation_agent_implements_protocol(self) -> None:
        from vectraxis.agents.specialized.recommendation import RecommendationAgent

        agent = RecommendationAgent(llm=FakeLLMProvider())
        assert isinstance(agent, Agent)

    def test_recommendation_agent_type(self) -> None:
        from vectraxis.agents.specialized.recommendation import RecommendationAgent

        agent = RecommendationAgent(llm=FakeLLMProvider())
        assert agent.agent_type == AgentType.RECOMMENDATION

    def test_recommendation_agent_execute_returns_result(self) -> None:
        from vectraxis.agents.specialized.recommendation import RecommendationAgent

        agent = RecommendationAgent(llm=FakeLLMProvider())
        task = AgentTask(query="test query", agent_type=AgentType.RECOMMENDATION)
        result = agent.execute(task)
        assert isinstance(result, AgentResult)

    def test_recommendation_agent_uses_llm(self) -> None:
        from vectraxis.agents.specialized.recommendation import RecommendationAgent

        llm = FakeLLMProvider(responses={"Recommend": "top recommendations"})
        agent = RecommendationAgent(llm=llm)
        task = AgentTask(query="test query", agent_type=AgentType.RECOMMENDATION)
        result = agent.execute(task)
        assert result.output == "top recommendations"

    def test_recommendation_agent_passes_context(self) -> None:
        from vectraxis.agents.specialized.recommendation import RecommendationAgent

        llm = FakeLLMProvider(responses={"Recommend": "contextual recs"})
        agent = RecommendationAgent(llm=llm)
        task = AgentTask(query="test", agent_type=AgentType.RECOMMENDATION)
        context = ["doc1", "doc2"]
        result = agent.execute(task, context=context)
        assert result.output == "contextual recs"
        assert result.evidence == context
