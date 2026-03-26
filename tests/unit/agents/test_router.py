"""Tests for TaskRouter."""

import pytest

from vectraxis.agents.base import FakeLLMProvider
from vectraxis.agents.router import TaskRouter
from vectraxis.agents.specialized.analysis import AnalysisAgent
from vectraxis.agents.specialized.recommendation import RecommendationAgent
from vectraxis.agents.specialized.summarization import SummarizationAgent
from vectraxis.models.agent import AgentTask, AgentType


def _build_agents() -> dict[
    AgentType, AnalysisAgent | SummarizationAgent | RecommendationAgent
]:

    llm = FakeLLMProvider()
    return {
        AgentType.ANALYSIS: AnalysisAgent(llm=llm),
        AgentType.SUMMARIZATION: SummarizationAgent(llm=llm),
        AgentType.RECOMMENDATION: RecommendationAgent(llm=llm),
    }


class TestTaskRouter:
    def test_route_to_correct_agent(self) -> None:
        agents = _build_agents()
        router = TaskRouter(agents=agents)
        task = AgentTask(query="test", agent_type=AgentType.ANALYSIS)
        agent = router.route(task)
        assert agent.agent_type == AgentType.ANALYSIS

    def test_route_unknown_type_raises(self) -> None:
        router = TaskRouter(agents={})
        task = AgentTask(query="test", agent_type=AgentType.ANALYSIS)
        with pytest.raises(ValueError, match="No agent registered for type"):
            router.route(task)

    def test_route_all_agent_types(self) -> None:
        agents = _build_agents()
        router = TaskRouter(agents=agents)
        for agent_type in AgentType:
            task = AgentTask(query="test", agent_type=agent_type)
            agent = router.route(task)
            assert agent.agent_type == agent_type
