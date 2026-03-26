"""Agent base protocols and FakeLLMProvider for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from vectraxis.models.agent import AgentResult, AgentTask, AgentType


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    def generate(self, prompt: str, context: list[str] | None = None) -> str: ...


@runtime_checkable
class Agent(Protocol):
    """Protocol for agents that can execute tasks."""

    @property
    def agent_type(self) -> AgentType: ...

    def execute(
        self, task: AgentTask, context: list[str] | None = None
    ) -> AgentResult: ...


class FakeLLMProvider:
    """Deterministic LLM for testing. Returns preconfigured responses."""

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        default_response: str = "This is a fake response.",
    ):
        self._responses = responses or {}
        self._default_response = default_response

    def generate(self, prompt: str, context: list[str] | None = None) -> str:
        """Return a response based on keyword matching against the prompt."""
        for key, response in self._responses.items():
            if key in prompt:
                return response
        return self._default_response
