"""Tests for agent base protocols and FakeLLMProvider."""

from vectraxis.agents.base import Agent, FakeLLMProvider, LLMProvider


class TestLLMProviderProtocol:
    def test_llm_provider_is_protocol(self) -> None:
        """LLMProvider should be a runtime-checkable Protocol."""
        assert isinstance(FakeLLMProvider(), LLMProvider)

    def test_agent_is_protocol(self) -> None:
        """Agent should be a runtime-checkable Protocol."""
        from vectraxis.agents.specialized.analysis import AnalysisAgent

        agent = AnalysisAgent(llm=FakeLLMProvider())
        assert isinstance(agent, Agent)


class TestFakeLLMProvider:
    def test_fake_llm_default_response(self) -> None:
        """FakeLLMProvider should return default response when no keywords match."""
        llm = FakeLLMProvider()
        result = llm.generate("some prompt")
        assert result == "This is a fake response."

    def test_fake_llm_keyword_matching(self) -> None:
        """FakeLLMProvider returns configured response for keyword."""
        llm = FakeLLMProvider(
            responses={"analyze": "Analysis result", "summarize": "Summary result"}
        )
        result = llm.generate("Please analyze this data")
        assert result == "Analysis result"

    def test_fake_llm_with_context(self) -> None:
        """Context should not change the basic keyword-matching behavior."""
        llm = FakeLLMProvider(responses={"test": "test response"})
        result = llm.generate("test prompt", context=["ctx1", "ctx2"])
        assert result == "test response"

    def test_fake_llm_first_match_wins(self) -> None:
        """When multiple keywords match, the first one in dict order should win."""
        llm = FakeLLMProvider(responses={"alpha": "first", "beta": "second"})
        result = llm.generate("alpha beta prompt")
        assert result == "first"
